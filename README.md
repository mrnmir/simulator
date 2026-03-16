# simulator

A discrete-time network simulator for **Ambient IoT** research.  It models
base stations, battery-free Ambient IoT nodes, and the communication links
between them, providing a testbed for evaluating Ambient IoT network
deployments before real-life execution.

---

## Features

| Component | Description |
|-----------|-------------|
| **BaseStation** | RF transmitter that provides energy and connectivity to nearby IoT nodes. Supports configurable carrier frequency, transmit power, and coverage radius. |
| **AmbientIoTNode** | Battery-free IoT device that harvests energy from incoming RF signals and communicates via backscatter modulation. |
| **CommunicationLink** | Directional channel between two entities (downlink, uplink, or backscatter) with configurable bandwidth and latency. |
| **Network** | Simulator engine that manages topology, auto-connects nodes to their nearest base station, and drives time-stepped simulation. |

### RF propagation model

Free-space path loss (Friis transmission equation) is used throughout:

```
FSPL (dB) = 20 · log₁₀(4π · d · f / c)
```

where *d* is distance in metres, *f* is carrier frequency in Hz, and *c* is
the speed of light.

---

## Installation

Requires **Python ≥ 3.9**.

```bash
pip install -e ".[dev]"   # development install with pytest
```

---

## Quick start

```python
from simulator import Network, BaseStation, AmbientIoTNode

# Build a small network
net = Network()
net.add_base_station(BaseStation("bs0", x=0, y=0, coverage_radius_m=100))
net.add_iot_node(AmbientIoTNode("node0", x=30, y=0))
net.add_iot_node(AmbientIoTNode("node1", x=80, y=0))

# Auto-associate every node with its nearest covering base station
net.connect_all_nodes()

# Run 10 one-second simulation steps
results = net.run(steps=10, step_duration_s=1.0)

for r in results:
    print(f"Step {r.step}: harvested={r.harvested_energy_mj}, tx={r.transmissions}")

# Network-wide coverage summary
print(net.coverage_stats())
```

---

## Project layout

```
simulator/
├── pyproject.toml          # project metadata & build config
├── simulator/
│   ├── __init__.py         # public API
│   ├── utils.py            # RF propagation helpers (FSPL, dBm conversions)
│   ├── base_station.py     # BaseStation class
│   ├── iot_node.py         # AmbientIoTNode class
│   ├── link.py             # CommunicationLink class & LinkType enum
│   └── network.py          # Network simulator engine
└── tests/
    ├── test_utils.py
    ├── test_base_station.py
    ├── test_iot_node.py
    ├── test_link.py
    └── test_network.py
```

---

## Running tests

```bash
pytest
```
