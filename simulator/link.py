"""Communication link model for the Ambient IoT network simulator."""

from dataclasses import dataclass
from enum import Enum

from .utils import free_space_path_loss_db


class LinkType(str, Enum):
    """Direction / modulation type of a communication link."""

    DOWNLINK = "downlink"      # base station → node  (continuous RF broadcast)
    UPLINK = "uplink"          # node → base station  (backscatter)
    BACKSCATTER = "backscatter"  # alias for uplink backscatter direction


@dataclass
class CommunicationLink:
    """A directional communication link between two network entities.

    A link models the physical channel between a source and a target,
    capturing bandwidth, latency, and propagation characteristics.

    Attributes:
        link_id: Unique string identifier.
        source_id: ID of the transmitting entity (station or node).
        target_id: ID of the receiving entity (node or station).
        link_type: Direction / modulation type (see :class:`LinkType`).
        bandwidth_bps: Maximum data rate in bits-per-second.
        latency_ms: One-way propagation + processing latency in milliseconds.
        is_active: Whether the link is currently usable.
    """

    link_id: str
    source_id: str
    target_id: str
    link_type: LinkType = LinkType.DOWNLINK
    bandwidth_bps: float = 1_000.0
    latency_ms: float = 1.0
    is_active: bool = True

    def path_loss_db(self, distance_m: float, frequency_hz: float) -> float:
        """Return the free-space path loss (dB) for this link.

        Args:
            distance_m: Separation between source and target in metres.
            frequency_hz: Carrier frequency in Hz.

        Returns:
            Path loss in dB.
        """
        return free_space_path_loss_db(distance_m, frequency_hz)

    def throughput_bps(self) -> float:
        """Return effective throughput; 0 when the link is inactive."""
        return self.bandwidth_bps if self.is_active else 0.0
