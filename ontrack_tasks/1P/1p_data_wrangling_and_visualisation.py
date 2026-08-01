from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CSV_PATH = Path(__file__).with_name("restaurant_pest_capture_data.csv")

# Define function 
def analyse_capture_data(csv_path: Path = CSV_PATH) -> None:
    """Load, validate, and summarise the PIR movement capture data."""
    data = pd.read_csv(csv_path)
    
    # Validate CSV data
    required_columns = {"timestamp", "has_captured_movement"}
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(f"Missing CSV columns: {', '.join(sorted(missing_columns))}")

    # Preserve the original values so conversion problems can be reported.
    parsed_timestamps = pd.to_datetime(data["timestamp"], errors="coerce")
    parsed_movement = pd.to_numeric(
        data["has_captured_movement"], errors="coerce"
    )
    
    duplicate_timestamps = data.duplicated(subset="timestamp", keep=False)
    invalid_timestamps = parsed_timestamps.isna()
    invalid_movement = parsed_movement.isna() | ~parsed_movement.isin([0, 1])
    
    # Print basic stats to the terminal (conditionally).
    print(f"CSV file: {csv_path}")
    print(f"Rows read: {len(data)}")
    print(f"Duplicate timestamp rows: {duplicate_timestamps.sum()}")
    print(f"Invalid timestamps: {invalid_timestamps.sum()}")
    print(f"Invalid movement values: {invalid_movement.sum()}")

    if duplicate_timestamps.any():
        print("\nRows with duplicate timestamps:")
        print(data.loc[duplicate_timestamps].to_string(index=False))

    valid = data.loc[~invalid_timestamps & ~invalid_movement].copy()
    valid["timestamp"] = parsed_timestamps[~invalid_timestamps & ~invalid_movement]
    valid["has_captured_movement"] = parsed_movement[
        ~invalid_timestamps & ~invalid_movement
    ].astype(int)
    valid = valid.drop_duplicates(subset="timestamp").sort_values("timestamp")

    if valid.empty:
        print("\nNo valid data is available for calculating statistics.")
        return
    
    # Format and stats such as occurrences, time/end of capture, and capture duration.
    occurrences = int(valid["has_captured_movement"].sum())
    capture_start = valid["timestamp"].min()
    capture_end = valid["timestamp"].max()
    captured_duration = capture_end - capture_start

    # The task simulation maps each captured minute to one real-world hour.
    represented_hours = captured_duration.total_seconds() / 60

    print("\nBasic statistics")
    print(f"Movement occurrences: {occurrences}")
    print(f"Capture period: {capture_start} to {capture_end}")
    print(f"Captured duration: {captured_duration}")
    print(f"Represented real-world time: {represented_hours:.2f} hours")

    if represented_hours > 0:
        print(f"Occurrences per represented hour: {occurrences / represented_hours:.2f}")

    # One minute of captured time represents one hour of real-world time.
    valid["simulated_hour"] = (
        valid["timestamp"] - capture_start
    ).dt.total_seconds() / 60
    valid["cumulative_occurrences"] = valid["has_captured_movement"].cumsum()

    # Group events into simulated hours (captured minutes) for the bar chart.
    valid["hour_number"] = valid["simulated_hour"].astype(int) + 1
    occurrences_by_hour = valid.groupby("hour_number")[
        "has_captured_movement"
    ].sum()
    all_hours = range(1, int(valid["hour_number"].max()) + 1)
    occurrences_by_hour = occurrences_by_hour.reindex(all_hours, fill_value=0)

    figure, axes = plt.subplots(2, 1, figsize=(10, 8))

    axes[0].plot(
        valid["simulated_hour"],
        valid["cumulative_occurrences"],
        marker="o",
    )
    axes[0].set_title("Cumulative Movement Occurrences Over Time")
    axes[0].set_xlabel("Simulated time (hours)")
    axes[0].set_ylabel("Cumulative movement occurrences")
    axes[0].grid(True, alpha=0.3)

    axes[1].bar(occurrences_by_hour.index, occurrences_by_hour.values)
    axes[1].set_title("Movement Occurrences per Simulated Hour")
    axes[1].set_xlabel("Simulated hour")
    axes[1].set_ylabel("Movement occurrences")
    axes[1].set_xticks(occurrences_by_hour.index)
    axes[1].grid(axis="y", alpha=0.3)

    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    analyse_capture_data()
