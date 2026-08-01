# Task 1P - Receive & Process PIR Sensor Data
# Author: Jason Mark Vellucci | SID: 221437402

import serial
import csv
import time
from datetime import datetime

end_time = time.time() + (60 * 10)
ser = serial.Serial('/dev/cu.usbserial-0001', 115200, timeout=1)

with open('restaurant_pest_capture_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'has_captured_movement'])
    
    while time.time() < end_time:
        line = ser.readline().decode()
        if not line:
            continue
        timestamp = datetime.now().isoformat()
        writer.writerow([timestamp, line.strip()])
        print(f"{timestamp}: {line.strip()}")