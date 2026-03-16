"""Tests for the BaseStation class."""

import math
import pytest

from simulator.base_station import BaseStation


@pytest.fixture
def station():
    return BaseStation(
        station_id="bs0",
        x=0.0,
        y=0.0,
        frequency_hz=915e6,
        tx_power_dbm=30.0,
        coverage_radius_m=100.0,
    )


class TestBaseStationDistance:
    def test_same_position(self, station):
        assert station.distance_to(0, 0) == 0.0

    def test_distance_along_x(self, station):
        assert station.distance_to(30.0, 0.0) == pytest.approx(30.0)

    def test_distance_diagonal(self, station):
        assert station.distance_to(3.0, 4.0) == pytest.approx(5.0)


class TestBaseStationCoverage:
    def test_inside_coverage(self, station):
        assert station.is_in_coverage(50.0, 0.0) is True

    def test_on_edge_of_coverage(self, station):
        assert station.is_in_coverage(100.0, 0.0) is True

    def test_outside_coverage(self, station):
        assert station.is_in_coverage(101.0, 0.0) is False


class TestReceivedPower:
    def test_at_zero_distance(self, station):
        assert station.received_power_dbm(0.0) == 30.0

    def test_decreases_with_distance(self, station):
        p10 = station.received_power_dbm(10.0)
        p20 = station.received_power_dbm(20.0)
        assert p10 > p20

    def test_inverse_square_law(self, station):
        # Doubling distance ⟹ ~6 dB lower received power
        p10 = station.received_power_dbm(10.0)
        p20 = station.received_power_dbm(20.0)
        assert abs((p10 - p20) - 6.02) < 0.1

    def test_negative_distance_raises(self, station):
        with pytest.raises(ValueError):
            station.received_power_dbm(-1.0)


class TestBaseStationDefaults:
    def test_default_frequency(self):
        bs = BaseStation("bs1", 0, 0)
        assert bs.frequency_hz == 915e6

    def test_default_tx_power(self):
        bs = BaseStation("bs1", 0, 0)
        assert bs.tx_power_dbm == 30.0

    def test_connected_node_ids_empty_by_default(self):
        bs = BaseStation("bs1", 0, 0)
        assert bs.connected_node_ids == []
