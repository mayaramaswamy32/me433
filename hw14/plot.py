import sys
import serial
import time
import matplotlib.pyplot as plt
import numpy as np


if len(sys.argv) < 2:
    print("Usage: hx_plot.py <serial_port> [baudrate]")
    sys.exit()

port = sys.argv[1]
baud = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
NUM_LINES = 5*80

def read_lines(ser, n):
    lines = []
    start = time.time()
    while len(lines) < n and (time.time() - start) < 50.0:
        line = ser.readline()
        if not line:
            continue
        try:
            s = line.decode('utf-8', errors='replace').strip()
        except Exception:
            continue
        if s:
            lines.append(s)
    return lines

with serial.Serial(port, baud, timeout=10) as ser:
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    print("Collection requested...")
    
    ser.write(f"{NUM_LINES}\n".encode('utf-8'))
    ser.flush()
    
    raw_lines = read_lines(ser, NUM_LINES)
    print("Collected" + str(len(raw_lines))+" lines")
    if len(raw_lines) < NUM_LINES:
        print(f"Warning: expected {NUM_LINES} lines, got {len(raw_lines)}")

times = []
raw_values = []
filt_values = []
for ln in raw_lines:
    parts = ln.split()
    if len(parts) < 3:
        continue
    try:
        t    = float(parts[0])
        raw  = float(parts[1])
        filt = float(parts[2])
    except ValueError:
        continue
    times.append(t)
    raw_values.append(raw)
    filt_values.append(filt)

if not times:
    print("No valid data parsed.")
    sys.exit(1)
    
if times:
    base = times[0]
    for i in range(len(times)):
        times[i] -= base
        times[i] = times[i]/1000

# plot raw and filtered vs time
plt.figure(figsize=(8,4))
plt.plot(times, raw_values, label='Raw', marker='o', linestyle='-')
plt.plot(times, filt_values, label='Filtered', marker='o', linestyle='-')
plt.xlabel('Time (s)')
plt.ylabel('Value')
plt.title('HX711 values vs time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

Fs = len(times)/(times[-1]-times[0]) # sample rate
Ts = 1.0/Fs                          # sampling interval
print("Sample rate = "+str(Fs))
ts = np.arange(0, times[-1], Ts)     # time vector

n = len(raw_values)
k = np.arange(n)
T = n/Fs
frq = k/T
frq = frq[range(int(n/2))]

# FFT of raw
Y_raw = np.fft.fft(raw_values)/n
Y_raw = Y_raw[range(int(n/2))]

# FFT of filtered
Y_filt = np.fft.fft(filt_values)/n
Y_filt = Y_filt[range(int(n/2))]

fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.loglog(frq, abs(Y_raw),  'b', label='Raw')
ax1.loglog(frq, abs(Y_filt), 'r', label='Filtered')
ax1.set_xlabel('Freq (Hz)')
ax1.set_ylabel('|Y(freq)|')
ax1.set_title('FFT')
ax1.legend()

ax2.plot(times, raw_values,  'b', label='Raw')
ax2.plot(times, filt_values, 'r', label='Filtered')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Amplitude')
ax2.set_title('Time Domain')
ax2.legend()

plt.tight_layout()
plt.show()