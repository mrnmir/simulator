"""Tests for the AmbientIoTNode class."""

import pytest

from simulator.iot_node import AmbientIoTNode


@pytest.fixture
def node():
    return AmbientIoTNode(
        node_id="node0",
        x=30.0,
        y=0.0,
        energy_capacity_mj=1.0,
        energy_level_mj=0.0,
        harvest_efficiency=0.5,
        sensitivity_dbm=-20.0,
        tx_energy_cost_mj=0.1,
    )


class TestEnergyHarvesting:
    def test_harvest_above_sensitivity(self, node):
        harvested = node.harvest_energy(received_power_dbm=0.0, duration_s=1.0)
        assert harvested > 0.0
        assert node.energy_level_mj == pytest.approx(harvested)

    def test_no_harvest_below_sensitivity(self, node):
        harvested = node.harvest_energy(received_power_dbm=-25.0, duration_s=1.0)
        assert harvested == 0.0
        assert node.energy_level_mj == 0.0

    def test_harvest_capped_at_capacity(self, node):
        # Very strong signal for very long time – must not exceed capacity
        node.harvest_energy(received_power_dbm=30.0, duration_s=10_000.0)
        assert node.energy_level_mj <= node.energy_capacity_mj

    def test_negative_duration_raises(self, node):
        with pytest.raises(ValueError):
            node.harvest_energy(received_power_dbm=0.0, duration_s=-1.0)

    def test_zero_duration_harvests_nothing(self, node):
        harvested = node.harvest_energy(received_power_dbm=30.0, duration_s=0.0)
        assert harvested == 0.0


class TestTransmission:
    def test_cannot_transmit_when_empty(self, node):
        assert node.can_transmit() is False
        assert node.transmit() is False

    def test_can_transmit_with_sufficient_energy(self, node):
        node.energy_level_mj = 0.5
        assert node.can_transmit() is True
        success = node.transmit()
        assert success is True
        assert node.energy_level_mj == pytest.approx(0.4)

    def test_transmit_deducts_energy(self, node):
        node.energy_level_mj = 0.3
        node.transmit()
        assert node.energy_level_mj == pytest.approx(0.2)

    def test_transmit_stores_payload(self, node):
        node.energy_level_mj = 1.0
        node.transmit(payload="sensor_data")
        assert "sensor_data" in node.data_buffer

    def test_transmit_empty_payload_not_stored(self, node):
        node.energy_level_mj = 1.0
        node.transmit(payload="")
        assert node.data_buffer == []


class TestEnergyFraction:
    def test_full_energy(self, node):
        node.energy_level_mj = node.energy_capacity_mj
        assert node.energy_fraction == pytest.approx(1.0)

    def test_empty_energy(self, node):
        node.energy_level_mj = 0.0
        assert node.energy_fraction == pytest.approx(0.0)

    def test_half_energy(self, node):
        node.energy_level_mj = 0.5
        assert node.energy_fraction == pytest.approx(0.5)
