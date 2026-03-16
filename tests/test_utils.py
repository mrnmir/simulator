"""Tests for RF utility functions."""

import math
import pytest

from simulator.utils import free_space_path_loss_db, dbm_to_watts, watts_to_dbm


class TestFreeSpacePathLoss:
    def test_known_value(self):
        # At 1 m and 1 GHz: FSPL = 20*log10(4π*1*1e9/3e8) ≈ 32.44 dB
        result = free_space_path_loss_db(1.0, 1e9)
        assert abs(result - 32.44) < 0.1

    def test_doubles_with_distance(self):
        # Doubling distance adds ~6 dB
        pl1 = free_space_path_loss_db(10.0, 915e6)
        pl2 = free_space_path_loss_db(20.0, 915e6)
        assert abs((pl2 - pl1) - 6.02) < 0.1

    def test_invalid_distance(self):
        with pytest.raises(ValueError):
            free_space_path_loss_db(0, 915e6)
        with pytest.raises(ValueError):
            free_space_path_loss_db(-1, 915e6)

    def test_invalid_frequency(self):
        with pytest.raises(ValueError):
            free_space_path_loss_db(10, 0)
        with pytest.raises(ValueError):
            free_space_path_loss_db(10, -1e9)


class TestDbmConversions:
    def test_dbm_to_watts_0dbm(self):
        assert abs(dbm_to_watts(0) - 1e-3) < 1e-9

    def test_dbm_to_watts_30dbm(self):
        assert abs(dbm_to_watts(30) - 1.0) < 1e-9

    def test_dbm_to_watts_negative(self):
        assert dbm_to_watts(-30) == pytest.approx(1e-6, rel=1e-6)

    def test_watts_to_dbm_1w(self):
        assert abs(watts_to_dbm(1.0) - 30.0) < 1e-9

    def test_watts_to_dbm_1mw(self):
        assert abs(watts_to_dbm(1e-3) - 0.0) < 1e-9

    def test_watts_to_dbm_invalid(self):
        with pytest.raises(ValueError):
            watts_to_dbm(0)
        with pytest.raises(ValueError):
            watts_to_dbm(-1)

    def test_round_trip(self):
        for dbm in [-30, 0, 10, 30]:
            assert watts_to_dbm(dbm_to_watts(dbm)) == pytest.approx(dbm, abs=1e-9)
