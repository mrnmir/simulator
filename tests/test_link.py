"""Tests for the CommunicationLink class."""

import pytest

from simulator.link import CommunicationLink, LinkType


@pytest.fixture
def downlink():
    return CommunicationLink(
        link_id="dl_bs0_node0",
        source_id="bs0",
        target_id="node0",
        link_type=LinkType.DOWNLINK,
        bandwidth_bps=1000.0,
        latency_ms=2.0,
        is_active=True,
    )


class TestThroughput:
    def test_active_link_returns_bandwidth(self, downlink):
        assert downlink.throughput_bps() == 1000.0

    def test_inactive_link_returns_zero(self, downlink):
        downlink.is_active = False
        assert downlink.throughput_bps() == 0.0


class TestPathLoss:
    def test_positive_path_loss(self, downlink):
        pl = downlink.path_loss_db(distance_m=50.0, frequency_hz=915e6)
        assert pl > 0.0

    def test_path_loss_increases_with_distance(self, downlink):
        pl10 = downlink.path_loss_db(50.0, 915e6)
        pl20 = downlink.path_loss_db(100.0, 915e6)
        assert pl20 > pl10


class TestLinkType:
    def test_default_link_type(self):
        link = CommunicationLink(link_id="lnk", source_id="a", target_id="b")
        assert link.link_type == LinkType.DOWNLINK

    def test_backscatter_link_type(self):
        link = CommunicationLink(
            link_id="ul",
            source_id="node0",
            target_id="bs0",
            link_type=LinkType.BACKSCATTER,
        )
        assert link.link_type == LinkType.BACKSCATTER

    def test_link_type_string_value(self):
        assert LinkType.DOWNLINK == "downlink"
        assert LinkType.UPLINK == "uplink"
        assert LinkType.BACKSCATTER == "backscatter"
