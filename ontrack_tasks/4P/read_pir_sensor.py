import serial
import base64
import firebase_admin

from firebase_admin import credentials, db
from datetime import datetime, timezone


# --------------------------------------------------
# Configuration
# --------------------------------------------------

SERIAL_PORT = "COM5"
BAUD_RATE = 115200

SENSOR_ID = "PIR_CAM_01"

SERVICE_ACCOUNT_FILE = ""

DATABASE_URL = ""


# --------------------------------------------------
# Firebase
# --------------------------------------------------

cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)

firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": DATABASE_URL
    }
)


# --------------------------------------------------
# Serial
# --------------------------------------------------

ser = serial.Serial(
    port=SERIAL_PORT,
    baudrate=BAUD_RATE,
    timeout=5
)

print("Waiting for ESP32...")


# --------------------------------------------------
# Helper: read an exact number of bytes
# --------------------------------------------------

def read_exactly(serial_connection, number_of_bytes):

    data = bytearray()

    while len(data) < number_of_bytes:

        chunk = serial_connection.read(
            number_of_bytes - len(data)
        )

        if not chunk:
            raise TimeoutError(
                "Timed out while receiving image."
            )

        data.extend(chunk)

    return bytes(data)


# --------------------------------------------------
# Main loop
# --------------------------------------------------

while True:

    try:

        # Read ESP32 text header
        line = (
            ser.readline()
            .decode("utf-8", errors="ignore")
            .strip()
        )

        if not line:
            continue

        print("ESP32:", line)

        # Expected:
        #
        # EVENT:1:17248
        #
        if line.startswith("EVENT:"):

            parts = line.split(":")

            if len(parts) != 3:
                print("Invalid event header.")
                continue

            movement = int(parts[1])
            image_size = int(parts[2])

            print(
                f"Movement detected. "
                f"Receiving {image_size} image bytes..."
            )

            # ------------------------------------------
            # Receive JPEG
            # ------------------------------------------

            image_bytes = read_exactly(
                ser,
                image_size
            )

            print(
                f"Received {len(image_bytes)} bytes."
            )


            # ------------------------------------------
            # Convert JPEG to Base64
            # ------------------------------------------

            image_base64 = base64.b64encode(
                image_bytes
            ).decode("utf-8")


            # ------------------------------------------
            # Build Firebase record
            # ------------------------------------------

            record = {
                "sensor_id": SENSOR_ID,
                "movement": movement,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
                "image_base64": image_base64
            }


            # ------------------------------------------
            # Store in Realtime Database
            # ------------------------------------------

            reference = db.reference(
                "movement_events"
            )

            new_record = reference.push(record)

            print(
                "Stored Firebase event:",
                new_record.key
            )


    except KeyboardInterrupt:

        print("\nStopping.")
        ser.close()
        break


    except Exception as error:

        print("ERROR:", error)