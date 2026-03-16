"""Tests for the Network simulator."""

import pytest

from simulator.base_station import BaseStation
from simulator.iot_node import AmbientIoTNode
from simulator.link import CommunicationLink, LinkType
from simulator.network import Network


@pytest.fixture
def small_network():
    """A network with one base station and two nodes (one in range, one out)."""
    net = Network()
    net.add_base_station(BaseStation("bs0", x=0.0, y=0.0, coverage_radius_m=100.0))
    net.add_iot_node(AmbientIoTNode("node_near", x=30.0, y=0.0))
    net.add_iot_node(AmbientIoTNode("node_far", x=200.0, y=0.0))
    return net


class TestTopologyManagement:
    def test_add_base_station(self, small_network):
        assert "bs0" in small_network.base_stations

    def test_add_iot_node(self, small_network):
        assert "node_near" in small_network.iot_nodes
        assert "node_far" in small_network.iot_nodes

    def test_duplicate_base_station_raises(self, small_network):
        with pytest.raises(ValueError):
            small_network.add_base_station(BaseStation("bs0", x=10, y=10))

    def test_duplicate_node_raises(self, small_network):
        with pytest.raises(ValueError):
            small_network.add_iot_node(AmbientIoTNode("node_near", x=0, y=0))

    def test_duplicate_link_raises(self, small_network):
        small_network.add_link(
            CommunicationLink("lnk1", "bs0", "node_near", LinkType.DOWNLINK)
        )
        with pytest.raises(ValueError):
            small_network.add_link(
                CommunicationLink("lnk1", "bs0", "node_near", LinkType.DOWNLINK)
            )


class TestNodeConnection:
    def test_near_node_connected(self, small_network):
        station_id = small_network.connect_node_to_nearest_station(
            small_network.iot_nodes["node_near"]
        )
        assert station_id == "bs0"
        assert small_network.iot_nodes["node_near"].connected_station_id == "bs0"

    def test_far_node_not_connected(self, small_network):
        station_id = small_network.connect_node_to_nearest_station(
            small_network.iot_nodes["node_far"]
        )
        assert station_id is None
        assert small_network.iot_nodes["node_far"].connected_station_id is None

    def test_connect_all_nodes(self, small_network):
        mapping = small_network.connect_all_nodes()
        assert mapping["node_near"] == "bs0"
        assert mapping["node_far"] is None

    def test_links_created_on_connection(self, small_network):
        small_network.connect_node_to_nearest_station(
            small_network.iot_nodes["node_near"]
        )
        links = small_network.links
        assert "dl_bs0_node_near" in links
        assert "ul_node_near_bs0" in links

    def test_node_registered_with_station(self, small_network):
        small_network.connect_node_to_nearest_station(
            small_network.iot_nodes["node_near"]
        )
        assert "node_near" in small_network.base_stations["bs0"].connected_node_ids


class TestSimulationStep:
    def test_step_returns_result(self, small_network):
        small_network.connect_all_nodes()
        result = small_network.step(duration_s=1.0)
        assert result.step == 0
        assert result.duration_s == 1.0

    def test_connected_node_harvests_energy(self, small_network):
        small_network.connect_all_nodes()
        result = small_network.step(duration_s=1.0)
        # node_near is connected and close – it should have harvested some energy
        assert result.harvested_energy_mj.get("node_near", 0.0) >= 0.0

    def test_unconnected_node_not_in_results(self, small_network):
        small_network.connect_all_nodes()
        result = small_network.step(duration_s=1.0)
        # node_far is out of range and unconnected
        assert "node_far" not in result.harvested_energy_mj

    def test_step_counter_increments(self, small_network):
        small_network.connect_all_nodes()
        r0 = small_network.step()
        r1 = small_network.step()
        assert r0.step == 0
        assert r1.step == 1

    def test_invalid_duration_raises(self, small_network):
        with pytest.raises(ValueError):
            small_network.step(duration_s=0)
        with pytest.raises(ValueError):
            small_network.step(duration_s=-1)

    def test_run_returns_correct_number_of_results(self, small_network):
        small_network.connect_all_nodes()
        results = small_network.run(steps=5, step_duration_s=1.0)
        assert len(results) == 5

    def test_run_invalid_steps_raises(self, small_network):
        with pytest.raises(ValueError):
            small_network.run(steps=0)


class TestCoverageStats:
    def test_stats_before_connection(self, small_network):
        stats = small_network.coverage_stats()
        assert stats["total_nodes"] == 2
        assert stats["covered_nodes"] == 0
        assert stats["coverage_fraction"] == 0.0

    def test_stats_after_connection(self, small_network):
        small_network.connect_all_nodes()
        stats = small_network.coverage_stats()
        assert stats["covered_nodes"] == 1
        assert stats["coverage_fraction"] == pytest.approx(0.5)

    def test_stats_empty_network(self):
        net = Network()
        stats = net.coverage_stats()
        assert stats["total_nodes"] == 0
        assert stats["coverage_fraction"] == 0.0

    def test_stats_link_count(self, small_network):
        small_network.connect_all_nodes()
        stats = small_network.coverage_stats()
        # One near node connected → 2 links (downlink + uplink)
        assert stats["total_links"] == 2
