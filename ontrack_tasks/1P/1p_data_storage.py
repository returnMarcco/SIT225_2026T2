# Task 1P - Receive & Process PIR Sensor Data
# Author: Jason Mark Vellucci | SID: 221437402

# Import various libraries
import serial
import csv
import time
from datetime import datetime

# Set end-time for loop to finish
end_time = time.time() + (60 * 10)

# Create serial connection with suitable baud rate
ser = serial.Serial('/dev/cu.usbserial-0001', 115200, timeout=1)

# Open the stated CSV file, set options
with open('restaurant_pest_capture_data.csv', 'w', newline='') as f:
    writer = csv.writer(f) # Return the CSV writer
    writer.writerow(['timestamp', 'has_captured_movement']) # Write headers
    
    # While end time > current time, read input from serial,
    # if input isn't empty, generate timestamp, write the row (positional, based on array elements),
    # then print to the terminal. If input is empty, continue to the next iteration of the loop.
    while time.time() < end_time:
        line = ser.readline().decode()
        if not line:
            continue
        timestamp = datetime.now().isoformat()
        writer.writerow([timestamp, line.strip()])
        print(f"{timestamp}: {line.strip()}")