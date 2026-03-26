
from iot_simulator.simulator import Simulator
from iot_simulator.metrics import save_to_csv, plot_signal_over_time, plot_connections, plot_positions
import matplotlib.pyplot as plt
from iot_simulator.devices import BaseStation, UserDevice


# Create base stations
stations = [
    BaseStation(id=1, x=200, y=200, frequency=1800, transmit_power=40),
    BaseStation(id=2, x=800, y=200, frequency=1800, transmit_power=40),
    BaseStation(id=3, x=500, y=800, frequency=1800, transmit_power=40),
]

# Create user devices
devices = [
    UserDevice(id=i, x=500, y=500, speed=30)
    for i in range(1, 15)
]

# Run simulation
sim = Simulator(stations, devices, area_size=1000)
history = sim.run(n_steps=50)

# Save and plot results
save_to_csv(history)
plot_signal_over_time(history)
plot_connections(history)
plot_positions(history, stations)
plt.show()