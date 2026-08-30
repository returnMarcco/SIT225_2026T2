"""
    Requirement: arduino_iot_cloud
    Install: pip install arduino-iot-cloud

    @Ahsan Habib
    School of IT, Deakin University, Australia.
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path

from arduino_iot_cloud import ArduinoCloudClient

DEVICE_ID = "d050961e-4e84-477d-b41f-f074b03b917f"
SECRET_KEY = "@@!TL4881CXuHYNXYZw5Ne!w2"
CSV_FILE = Path(__file__).with_name("temperature_data.csv")


# Callback function on temperature change event.
#
def on_temperature_changed(client, value, output_file):
    print(f"New temperature: {value}")
    timestamp = datetime.now().astimezone().isoformat()
    csv_row = f"{timestamp},{value}\n"
    output_file.write(csv_row)
    output_file.flush()


def main():
    print("main() function")

    # Instantiate Arduino cloud client
    client = ArduinoCloudClient(
        device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY
    )

    # Keep the file open while the cloud client runs. Append mode preserves
    # measurements already collected during earlier executions.
    with CSV_FILE.open("a", encoding="utf-8", newline="") as output_file:
        # Register with 'temperature' cloud variable and write changes to CSV.
        client.register(
            "temperature",
            value=None,
            on_write=lambda callback_client, value: on_temperature_changed(
                callback_client, value, output_file
            ),
        )

        # Start cloud client (this normally runs indefinitely).
        client.start()

if __name__ == "__main__":
    try:
        main()  # main function which runs in an internal infinite loop
    except Exception:
        traceback.print_exc(file=sys.stderr)
