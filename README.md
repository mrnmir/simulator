# IoT Network Simulator

[![Documentation Status](https://readthedocs.org/projects/iot-simulator/badge/?version=latest)](https://iot-simulator.readthedocs.io/en/latest/?badge=latest)

A simplistic network simulator for Ambient IoT networks, featuring base stations, user devices, and communication links. It serves as a testbed for evaluating signal propagation and connectivity before real-life hardware execution.

## Features

- **Base Stations & User Devices** — Define fixed base stations and mobile user devices with configurable parameters
- **Channel Modeling** — Free-space path loss calculations and received signal strength estimation
- **Simulation Engine** — Step-by-step simulation of device movement and signal connections
- **Metrics & Visualization** — Export results to CSV and generate plots for signal strength, connections, and device positions

## Installation

Requires Python 3.13+.

```bash
uv pip install -e .
```

## Usage

```python
from iot_simulator.simulator import Simulator
from iot_simulator.devices import BaseStation, UserDevice
from iot_simulator.metrics import save_to_csv, plot_signal_over_time, plot_connections, plot_positions

# Create base stations
stations = [
    BaseStation(id=1, x=200, y=200, frequency=1800, transmit_power=40),
    BaseStation(id=2, x=800, y=200, frequency=1800, transmit_power=40),
    BaseStation(id=3, x=500, y=800, frequency=1800, transmit_power=40),
]

# Create user devices
devices = [UserDevice(id=i, x=500, y=500, speed=30) for i in range(1, 15)]

# Run simulation
sim = Simulator(stations, devices, area_size=1000)
history = sim.run(n_steps=50)

# Save and plot results
save_to_csv(history)
plot_signal_over_time(history)
plot_connections(history)
plot_positions(history, stations)
```

## Documentation

Full documentation is available at [iot-simulator.readthedocs.io](https://iot-simulator.readthedocs.io).

To build docs locally:

```bash
uv pip install -e ".[docs]"
cd docs && make html
```

## Project Structure

```
iot_simulator/
├── devices.py      # BaseStation and UserDevice definitions
├── channel.py      # Signal propagation and path loss calculations
├── simulator.py    # Simulation engine
└── metrics.py      # CSV export and plotting utilities
```
