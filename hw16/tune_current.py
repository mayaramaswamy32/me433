# requires pyserial and matplotlib
# pip install pyserial matplotlib

import serial
import time
import matplotlib.pyplot as plt

# Your port - run `ls /dev/tty.usbmodem*` in terminal if this stops working
ser = serial.Serial('/dev/tty.usbmodem1102', 115200)
print('Opening port: ')
print(ser.name)

# Wait for STM32 to finish booting after the port-open reset
time.sleep(2)
 
# Send 'a' to trigger the current control run on the STM32
ser.write(b'a')
print("Sent 'a', waiting for data...")
 

# Read 400 lines back
read_samples = 0
ind     = []
desired = []
actual  = []

while read_samples < 399:
    data_read = ser.read_until(b'\n', 50)
    data_text = str(data_read, 'utf-8')
    print(data_text.strip())

    try:
        data = list(map(int, data_text.split()))
    except ValueError:
        continue

    if len(data) == 3:
        read_samples = data[0]
        ind.append(data[0])
        desired.append(data[1])
        actual.append(data[2])

# Plot it
plt.plot(ind, desired, 'b-', label='Desired')
plt.plot(ind, actual,  'r*-', label='Actual')
plt.ylabel('Current (raw INA219 units)')
plt.xlabel('Sample (1kHz)')
plt.title('Current Control Tuning: kp = -.009, ki = -.01')
plt.legend()
plt.grid(True)
plt.savefig('current_control.png', dpi=150)
plt.show()

ser.close()