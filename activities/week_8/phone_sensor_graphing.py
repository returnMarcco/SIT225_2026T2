import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"


def _plot_acceleration(axis):
    sensor_df = pd.read_csv(DATA_DIR / f"accel_{axis}.csv")
    sensor_df["time"] = pd.to_datetime(sensor_df["time"], format="mixed")

    figure, axis_plot = plt.subplots()
    axis_plot.plot(sensor_df["time"], sensor_df["value"])
    axis_plot.set_title(f"Accelerometer {axis.upper()} over time")
    axis_plot.set_xlabel("Time")
    axis_plot.set_ylabel("Acceleration")
    axis_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    figure.autofmt_xdate()
    figure.tight_layout()
    return figure


def accel_x():
    return _plot_acceleration("x")


def accel_y():
    return _plot_acceleration("y")


def accel_z():
    return _plot_acceleration("z")


def accel_combined_axis():
    figure, axis_plot = plt.subplots()

    for axis in ("x", "y", "z"):
        sensor_df = pd.read_csv(DATA_DIR / f"accel_{axis}.csv")
        sensor_df["time"] = pd.to_datetime(sensor_df["time"], format="mixed")
        axis_plot.plot(sensor_df["time"], sensor_df["value"], label=axis.upper())

    axis_plot.set_title("Accelerometer axes over time")
    axis_plot.set_xlabel("Time")
    axis_plot.set_ylabel("Acceleration")
    axis_plot.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    axis_plot.legend()
    figure.autofmt_xdate()
    figure.tight_layout()
    return figure


if __name__ == "__main__":
    accel_x()
    accel_y()
    accel_z()
    accel_combined_axis()
    plt.show()
