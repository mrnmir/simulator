"""Network simulator for Ambient IoT testbed.

Orchestrates base stations, Ambient IoT nodes, and communication links and
drives time-stepped simulation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .base_station import BaseStation
from .iot_node import AmbientIoTNode
from .link import CommunicationLink, LinkType


@dataclass
class StepResult:
    """Outcome of a single simulation time step.

    Attributes:
        step: Zero-based step index.
        duration_s: Simulated duration of this step in seconds.
        harvested_energy_mj: Mapping of node_id → energy harvested (mJ).
        transmissions: Mapping of node_id → transmission success flag.
        active_links: Number of links that were active during this step.
    """

    step: int
    duration_s: float
    harvested_energy_mj: Dict[str, float] = field(default_factory=dict)
    transmissions: Dict[str, bool] = field(default_factory=dict)
    active_links: int = 0


class Network:
    """Ambient IoT network simulator.

    Manages the network topology (base stations, nodes, links) and drives
    discrete-time simulation steps.

    Example::

        net = Network()
        bs = BaseStation("bs0", x=0, y=0)
        node = AmbientIoTNode("node0", x=30, y=0)
        net.add_base_station(bs)
        net.add_iot_node(node)
        net.connect_all_nodes()
        results = net.run(steps=10, step_duration_s=1.0)
    """

    def __init__(self) -> None:
        self._base_stations: Dict[str, BaseStation] = {}
        self._iot_nodes: Dict[str, AmbientIoTNode] = {}
        self._links: Dict[str, CommunicationLink] = {}
        self._step_count: int = 0

    # ------------------------------------------------------------------
    # Topology management
    # ------------------------------------------------------------------

    def add_base_station(self, station: BaseStation) -> None:
        """Add a base station to the network.

        Args:
            station: The :class:`BaseStation` to register.

        Raises:
            ValueError: If a station with the same ID already exists.
        """
        if station.station_id in self._base_stations:
            raise ValueError(
                f"Base station '{station.station_id}' already exists in the network."
            )
        self._base_stations[station.station_id] = station

    def add_iot_node(self, node: AmbientIoTNode) -> None:
        """Add an Ambient IoT node to the network.

        Args:
            node: The :class:`AmbientIoTNode` to register.

        Raises:
            ValueError: If a node with the same ID already exists.
        """
        if node.node_id in self._iot_nodes:
            raise ValueError(
                f"IoT node '{node.node_id}' already exists in the network."
            )
        self._iot_nodes[node.node_id] = node

    def add_link(self, link: CommunicationLink) -> None:
        """Add a communication link to the network.

        Args:
            link: The :class:`CommunicationLink` to register.

        Raises:
            ValueError: If a link with the same ID already exists.
        """
        if link.link_id in self._links:
            raise ValueError(
                f"Link '{link.link_id}' already exists in the network."
            )
        self._links[link.link_id] = link

    # ------------------------------------------------------------------
    # Read-only views
    # ------------------------------------------------------------------

    @property
    def base_stations(self) -> Dict[str, BaseStation]:
        """Read-only view of all registered base stations."""
        return dict(self._base_stations)

    @property
    def iot_nodes(self) -> Dict[str, AmbientIoTNode]:
        """Read-only view of all registered IoT nodes."""
        return dict(self._iot_nodes)

    @property
    def links(self) -> Dict[str, CommunicationLink]:
        """Read-only view of all registered links."""
        return dict(self._links)

    # ------------------------------------------------------------------
    # Association
    # ------------------------------------------------------------------

    def connect_node_to_nearest_station(
        self, node: AmbientIoTNode
    ) -> Optional[str]:
        """Associate *node* with the closest base station that covers it.

        Updates :attr:`AmbientIoTNode.connected_station_id` in-place and
        creates downlink + uplink :class:`CommunicationLink` objects if a
        covering station is found.

        Args:
            node: The node to connect.

        Returns:
            The station ID of the chosen base station, or None if no station
            covers the node.
        """
        best_station_id: Optional[str] = None
        best_distance = float("inf")

        for station in self._base_stations.values():
            d = station.distance_to(node.x, node.y)
            if d <= station.coverage_radius_m and d < best_distance:
                best_station_id = station.station_id
                best_distance = d

        if best_station_id is None:
            return None

        node.connected_station_id = best_station_id
        station = self._base_stations[best_station_id]

        # Register node with station
        if node.node_id not in station.connected_node_ids:
            station.connected_node_ids.append(node.node_id)

        # Create downlink and uplink automatically
        dl_id = f"dl_{best_station_id}_{node.node_id}"
        ul_id = f"ul_{node.node_id}_{best_station_id}"

        if dl_id not in self._links:
            self.add_link(
                CommunicationLink(
                    link_id=dl_id,
                    source_id=best_station_id,
                    target_id=node.node_id,
                    link_type=LinkType.DOWNLINK,
                )
            )
        if ul_id not in self._links:
            self.add_link(
                CommunicationLink(
                    link_id=ul_id,
                    source_id=node.node_id,
                    target_id=best_station_id,
                    link_type=LinkType.BACKSCATTER,
                )
            )

        return best_station_id

    def connect_all_nodes(self) -> Dict[str, Optional[str]]:
        """Connect every IoT node to its nearest covering base station.

        Returns:
            Mapping of node_id → station_id (or None if not covered).
        """
        return {
            nid: self.connect_node_to_nearest_station(node)
            for nid, node in self._iot_nodes.items()
        }

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------

    def step(self, duration_s: float = 1.0) -> StepResult:
        """Advance the simulation by one time step of *duration_s* seconds.

        Each step:
        1. Every connected node harvests energy from its base station's RF
           signal (using free-space path loss to compute received power).
        2. Every node that has sufficient energy attempts a backscatter
           transmission.

        Args:
            duration_s: Simulated duration in seconds. Must be > 0.

        Returns:
            A :class:`StepResult` summarising what happened during this step.

        Raises:
            ValueError: If duration_s is not positive.
        """
        if duration_s <= 0:
            raise ValueError(f"duration_s must be positive, got {duration_s}")

        result = StepResult(
            step=self._step_count,
            duration_s=duration_s,
        )

        for node_id, node in self._iot_nodes.items():
            if node.connected_station_id is None:
                continue
            station = self._base_stations.get(node.connected_station_id)
            if station is None:
                continue

            distance_m = station.distance_to(node.x, node.y)
            rx_power_dbm = station.received_power_dbm(distance_m)
            harvested = node.harvest_energy(rx_power_dbm, duration_s)
            result.harvested_energy_mj[node_id] = harvested

            success = node.transmit()
            result.transmissions[node_id] = success

        result.active_links = sum(
            1 for lnk in self._links.values() if lnk.is_active
        )

        self._step_count += 1
        return result

    def run(
        self, steps: int = 1, step_duration_s: float = 1.0
    ) -> List[StepResult]:
        """Run *steps* simulation steps and return all results.

        Args:
            steps: Number of time steps to simulate. Must be >= 1.
            step_duration_s: Duration of each step in seconds.

        Returns:
            List of :class:`StepResult` objects, one per step.

        Raises:
            ValueError: If steps < 1 or step_duration_s is not positive.
        """
        if steps < 1:
            raise ValueError(f"steps must be >= 1, got {steps}")
        return [self.step(step_duration_s) for _ in range(steps)]

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def coverage_stats(self) -> dict:
        """Return a summary of current network coverage.

        Returns:
            Dictionary with keys:
            - ``total_base_stations``: number of registered stations.
            - ``total_nodes``: number of registered IoT nodes.
            - ``covered_nodes``: nodes associated with a base station.
            - ``coverage_fraction``: *covered_nodes* / *total_nodes* (0–1).
            - ``total_links``: number of registered links.
        """
        total = len(self._iot_nodes)
        covered = sum(
            1
            for n in self._iot_nodes.values()
            if n.connected_station_id is not None
        )
        return {
            "total_base_stations": len(self._base_stations),
            "total_nodes": total,
            "covered_nodes": covered,
            "coverage_fraction": covered / total if total > 0 else 0.0,
            "total_links": len(self._links),
        }
