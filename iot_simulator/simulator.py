from iot_simulator.devices import BaseStation, UserDevice
from iot_simulator.channel import distance, free_space_path_loss, received_power


class Simulator:
    def __init__(self, stations: list[BaseStation], devices: list[UserDevice],
                 area_size: float = 1000.0):
        self.stations = stations
        self.devices = devices
        self.area_size = area_size
        self.time_step = 0
        self.history: list[dict] = []

    def _best_station(self, device: UserDevice) -> tuple[BaseStation, float]:
        """Find the station with the strongest signal for a device.

        Parameters
        ----------
        device : UserDevice
            The user device for which to find the best station.

        Returns
        -------
        tuple[BaseStation, float]
            The best station and its signal strength.
        """        
        best = None
        best_rssi = float("-inf")

        for station in self.stations:
            dist = distance(device.x, device.y, station.x, station.y)
            pl = free_space_path_loss(dist, station.frequency)
            rssi = received_power(station.transmit_power, pl)
            if rssi > best_rssi:
                best = station
                best_rssi = rssi

        return best, best_rssi

    def step(self) -> dict:
        """Run one time step of the simulation, moving devices and updating connections.

        Returns
        -------
        dict
            A dictionary containing the simulation results for the current time step:
            step: number of the time step
            avg_signal_dbm: average signal strength in dBm
            connections: dict mapping station id to number of connected devices
        """        
        self.time_step += 1

        # Move all devices
        for device in self.devices:
            device.move(self.area_size)

        # Connect each device to its best station
        connections: dict[int, list] = {s.id: [] for s in self.stations}
        signal_strengths = []

        for device in self.devices:
            station, rssi = self._best_station(device)
            connections[station.id].append(device.id)
            signal_strengths.append(rssi)

        avg_signal = sum(signal_strengths) / len(signal_strengths)
        record = {
            "step": self.time_step,
            "avg_signal_dbm": round(avg_signal, 2),
            "connections": {sid: len(devs) for sid, devs in connections.items()},
            "positions": [(d.x, d.y) for d in self.devices]
        }
        self.history.append(record)
        return record

    def run(self, n_steps: int) -> list[dict]:
        """Run the simulation for n steps."""
        for i in range(n_steps):
            record = self.step()
            print(f"Step {record['step']:3d} | "
                  f"Avg signal: {record['avg_signal_dbm']:7.2f} dBm | "
                  f"Connections: {record['connections']} | ")
        return self.history
