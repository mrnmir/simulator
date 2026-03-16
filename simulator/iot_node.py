"""Ambient IoT node model for the network simulator."""

from dataclasses import dataclass, field
from typing import List, Optional

from .utils import dbm_to_watts


@dataclass
class AmbientIoTNode:
    """An Ambient IoT node that harvests energy from RF signals and communicates
    via backscatter.

    Ambient IoT nodes are ultra-low-power devices that derive their operating
    energy entirely from ambient RF sources (e.g. the downlink signal from a
    nearby base station).  They respond by modulating and reflecting
    (backscattering) that same signal back to the base station.

    Attributes:
        node_id: Unique string identifier.
        x: Horizontal position in metres.
        y: Vertical position in metres.
        energy_capacity_mj: Maximum energy storage in milli-Joules.
        energy_level_mj: Current stored energy in milli-Joules.
        harvest_efficiency: Fraction of received RF power converted to stored
            energy (0 < η ≤ 1).
        sensitivity_dbm: Minimum received power (dBm) required to harvest energy
            and operate.
        tx_energy_cost_mj: Energy consumed per backscatter transmission in mJ.
        connected_station_id: ID of the associated base station, or None.
        data_buffer: Pending data packets waiting to be transmitted.
    """

    node_id: str
    x: float
    y: float
    energy_capacity_mj: float = 1.0
    energy_level_mj: float = 0.0
    harvest_efficiency: float = 0.5
    sensitivity_dbm: float = -20.0
    tx_energy_cost_mj: float = 0.1
    connected_station_id: Optional[str] = None
    data_buffer: List[str] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Energy management
    # ------------------------------------------------------------------

    def harvest_energy(self, received_power_dbm: float, duration_s: float) -> float:
        """Harvest energy from an incoming RF signal.

        If *received_power_dbm* is below :attr:`sensitivity_dbm` the node
        cannot operate and no energy is stored.

        Args:
            received_power_dbm: Received RF power at the node in dBm.
            duration_s: Duration of the RF exposure in seconds. Must be >= 0.

        Returns:
            Actual energy harvested in milli-Joules (may be less than the
            theoretical maximum if the energy store is nearly full).

        Raises:
            ValueError: If duration_s is negative.
        """
        if duration_s < 0:
            raise ValueError(f"duration_s must be >= 0, got {duration_s}")
        if received_power_dbm < self.sensitivity_dbm:
            return 0.0
        received_power_w = dbm_to_watts(received_power_dbm)
        # Theoretical energy = P × η × t, converted from J to mJ
        theoretical_mj = received_power_w * self.harvest_efficiency * duration_s * 1e3
        headroom_mj = self.energy_capacity_mj - self.energy_level_mj
        actual_mj = min(theoretical_mj, headroom_mj)
        self.energy_level_mj += actual_mj
        return actual_mj

    @property
    def energy_fraction(self) -> float:
        """Current energy level as a fraction of capacity (0.0 – 1.0)."""
        if self.energy_capacity_mj == 0:
            return 0.0
        return self.energy_level_mj / self.energy_capacity_mj

    # ------------------------------------------------------------------
    # Transmission
    # ------------------------------------------------------------------

    def can_transmit(self) -> bool:
        """Return True if the node has enough energy for a transmission."""
        return self.energy_level_mj >= self.tx_energy_cost_mj

    def transmit(self, payload: str = "") -> bool:
        """Attempt a backscatter transmission.

        Deducts :attr:`tx_energy_cost_mj` from the energy store on success.
        Optionally attaches *payload* to the internal data buffer for
        higher-level processing.

        Args:
            payload: Optional data string to record in the buffer.

        Returns:
            True if the transmission succeeded (enough energy was available),
            False otherwise.
        """
        if not self.can_transmit():
            return False
        self.energy_level_mj -= self.tx_energy_cost_mj
        if payload:
            self.data_buffer.append(payload)
        return True
