"""Base station model for the Ambient IoT network simulator."""

import math
from dataclasses import dataclass, field
from typing import List

from .utils import free_space_path_loss_db


@dataclass
class BaseStation:
    """A base station that provides RF coverage and energy to Ambient IoT nodes.

    The base station continuously broadcasts an RF signal that nearby
    AmbientIoTNodes can use for energy harvesting and backscatter communication.

    Attributes:
        station_id: Unique string identifier.
        x: Horizontal position in metres.
        y: Vertical position in metres.
        frequency_hz: Carrier frequency in Hz (default 915 MHz ISM band).
        tx_power_dbm: Transmit power in dBm (default 30 dBm = 1 W).
        coverage_radius_m: Maximum communication/harvesting radius in metres.
        connected_node_ids: IDs of nodes currently associated with this station.
    """

    station_id: str
    x: float
    y: float
    frequency_hz: float = 915e6
    tx_power_dbm: float = 30.0
    coverage_radius_m: float = 100.0
    connected_node_ids: List[str] = field(default_factory=list)

    def distance_to(self, x: float, y: float) -> float:
        """Return the Euclidean distance (metres) from the station to point (x, y)."""
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)

    def received_power_dbm(self, distance_m: float) -> float:
        """Return the received signal power (dBm) at *distance_m* from the station.

        Uses free-space path loss.  When distance_m is zero the transmit power
        is returned directly (no path loss).

        Args:
            distance_m: Distance from the station in metres. Must be >= 0.

        Returns:
            Received power in dBm.

        Raises:
            ValueError: If distance_m is negative.
        """
        if distance_m < 0:
            raise ValueError(f"distance_m must be >= 0, got {distance_m}")
        if distance_m == 0:
            return self.tx_power_dbm
        path_loss = free_space_path_loss_db(distance_m, self.frequency_hz)
        return self.tx_power_dbm - path_loss

    def is_in_coverage(self, x: float, y: float) -> bool:
        """Return True if point (x, y) is within the station's coverage radius."""
        return self.distance_to(x, y) <= self.coverage_radius_m
