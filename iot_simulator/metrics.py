import csv
import matplotlib.pyplot as plt


def save_to_csv(history: list[dict], filename: str = "results.csv"):
    """Save results to a csv file.

    Parameters
    ----------
    history : list[dict]
        The simulation history to save.
    filename : str, optional
        The name of the CSV file to save the results to, by default "results.csv"
    """    
    if not history:
        return

    # Collect all station IDs from the first record
    station_ids = sorted(history[0]["connections"].keys())

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["step", "avg_signal_dbm"] + [f"station_{sid}_devices" for sid in station_ids]
        writer.writerow(header)

        for record in history:
            row = [record["step"], record["avg_signal_dbm"]]
            row += [record["connections"].get(sid, 0) for sid in station_ids]
            writer.writerow(row)

    print(f"Results saved to {filename}")


def plot_signal_over_time(history: list[dict]):
    """Line chart of average signal strength per step

    Parameters
    ----------
    history : list[dict]
        The simulation history to plot.
    """    
    steps = [r["step"] for r in history]
    signals = [r["avg_signal_dbm"] for r in history]

    plt.figure(figsize=(8, 4))
    plt.plot(steps, signals, marker="o", markersize=3)
    plt.xlabel("Time Step")
    plt.ylabel("Avg Signal Strength (dBm)")
    plt.title("Average Signal Strength Over Time")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("plots/signal_over_time.png", dpi=300)


def plot_connections(history: list[dict]):
    """Bar chart of total device-connections per station across all steps.

    Parameters
    ----------
    history : list[dict]
        The simulation history to plot.
    """    
    
    station_ids = sorted(history[0]["connections"].keys())
    totals = {sid: 0 for sid in station_ids}

    for record in history:
        for sid, count in record["connections"].items():
            totals[sid] += count

    plt.figure(figsize=(8, 4))
    plt.bar([f"Station {sid}" for sid in station_ids], [totals[sid] for sid in station_ids])
    plt.xlabel("Base Station")
    plt.ylabel("Total Device-Connections")
    plt.title("Cumulative Connections Per Station")
    plt.tight_layout()
    plt.savefig("plots/connections_per_station.png", dpi=300)

def plot_positions(history: list[dict], stations: list):
    """Plot device trajectories and base station locations on a 2D grid.

    Parameters
    ----------
    history : list[dict]
        The simulation history containing positions per step.
    stations : list
        List of BaseStation objects.
    """
    plt.figure(figsize=(8, 8))

    # Plot each device's trajectory
    n_devices = len(history[0]["positions"])
    colors = plt.cm.tab10(range(n_devices))

    for i in range(n_devices):
        xs = [r["positions"][i][0] for r in history]
        ys = [r["positions"][i][1] for r in history]
        plt.plot(xs, ys, alpha=0.4, color=colors[i], linewidth=1)
        plt.scatter(xs[-1], ys[-1], color=colors[i], s=30,
                    label=f"Device {i + 1}", zorder=3)

    # Plot base stations
    for s in stations:
        plt.scatter(s.x, s.y, marker="^", s=200, c="red", edgecolors="black",
                    zorder=5)
        plt.annotate(f"BS {s.id}", (s.x, s.y), textcoords="offset points",
                     xytext=(5, 5), fontsize=9, fontweight="bold")

    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.title("Device Trajectories & Base Station Locations")
    plt.legend(fontsize=8, loc="upper right")
    plt.grid(True, alpha=0.3)
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig("plots/positions.png", dpi=300)