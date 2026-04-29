import csv
import matplotlib.pyplot as plt
import numpy as np

t = []
data = []

with open('sigD.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        t.append(float(row[0]))
        data.append(float(row[1]))

# sample rate
num_points = len(t)
total_time = t[-1] - t[0]
Fs = num_points / total_time

# FFT of original
y = np.array(data)
n = len(y)
k = np.arange(n)
T = n / Fs
frq = k / T
frq = frq[range(int(n/2))]
Y = np.fft.fft(y) / n
Y = Y[range(int(n/2))]

#! FIR Filter

# h = [
#     0.000316722757658048,
#     0.000648234662671191,
#     0.000994071907482014,
#     0.001353718146809975,
#     0.001726605439857885,
#     0.002112115390651698,
#     0.002509580484075452,
#     0.002918285614355949,
#     0.003337469801952409,
#     0.003766328094018759,
#     0.004204013642833450,
#     0.004649639955837712,
#     0.005102283310190595,
#     0.005560985324042011,
#     0.006024755676045751,
#     0.006492574963986844,
#     0.006963397692783875,
#     0.007436155381550404,
#     0.007909759778862694,
#     0.008383106174886126,
#     0.008855076798562298,
#     0.009324544287654996,
#     0.009790375219097763,
#     0.010251433686780583,
#     0.010706584913659601,
#     0.011154698884873204,
#     0.011594653988400937,
#     0.012025340649710043,
#     0.012445664946797693,
#     0.012854552192056211,
#     0.013250950467463546,
#     0.013633834099731757,
#     0.014002207062232068,
#     0.014355106290755580,
#     0.014691604900462549,
#     0.015010815291720185,
#     0.015311892132926604,
#     0.015594035208866314,
#     0.015856492123638117,
#     0.016098560847737677,
#     0.016319592099461971,
#     0.016518991551429295,
#     0.016696221853673313,
#     0.016850804465470645,
#     0.016982321288795219,
#     0.017090416097056676,
#     0.017174795753570320,
#     0.017235231215020401,
#     0.017271558316012153,
#     0.017283678331658725,
#     0.017271558316012153,
#     0.017235231215020401,
#     0.017174795753570320,
#     0.017090416097056676,
#     0.016982321288795219,
#     0.016850804465470645,
#     0.016696221853673313,
#     0.016518991551429295,
#     0.016319592099461971,
#     0.016098560847737677,
#     0.015856492123638117,
#     0.015594035208866314,
#     0.015311892132926604,
#     0.015010815291720185,
#     0.014691604900462549,
#     0.014355106290755580,
#     0.014002207062232068,
#     0.013633834099731757,
#     0.013250950467463546,
#     0.012854552192056211,
#     0.012445664946797693,
#     0.012025340649710043,
#     0.011594653988400937,
#     0.011154698884873204,
#     0.010706584913659601,
#     0.010251433686780583,
#     0.009790375219097763,
#     0.009324544287654996,
#     0.008855076798562298,
#     0.008383106174886126,
#     0.007909759778862694,
#     0.007436155381550404,
#     0.006963397692783875,
#     0.006492574963986842,
#     0.006024755676045751,
#     0.005560985324042011,
#     0.005102283310190595,
#     0.004649639955837712,
#     0.004204013642833450,
#     0.003766328094018759,
#     0.003337469801952409,
#     0.002918285614355949,
#     0.002509580484075452,
#     0.002112115390651697,
#     0.001726605439857885,
#     0.001353718146809975,
#     0.000994071907482014,
#     0.000648234662671191,
#     0.000316722757658048,
# ]

# M = len(h)
# fir = []
# for i in range(len(data)):
#     total = 0.0
#     for j in range(M):
#         if i - j >= 0:
#             total += h[j] * data[i - j]
#     fir.append(total)

# # FFT of FIR filtered
# fir_array = np.array(fir)
# Y_fir = np.fft.fft(fir_array) / n
# Y_fir = Y_fir[range(int(n/2))]

# # plot
# fig, (ax1, ax2) = plt.subplots(2, 1)
# ax1.plot(t, y, 'k', label='original')
# ax1.plot(t, fir, 'r', label='FIR filtered')
# ax1.set_xlabel('Time [s]')
# ax1.set_ylabel('Amplitude')
# ax1.set_title(f'sigD - FIR, {M} weights, cutoff=100Hz, BW=100')
# ax1.legend()

# ax2.loglog(frq, abs(Y), 'k', label='original')
# ax2.loglog(frq, abs(Y_fir), 'r', label='FIR filtered')
# ax2.set_xlabel('Freq (Hz)')
# ax2.set_ylabel('|Y(freq)|')
# ax2.set_title('FFT comparison')
# ax2.legend()

# plt.tight_layout()
# plt.show()


#! IIR Filter
A = 0.998
B = 1 - A  # so A+B=1

iir = [data[0]]  # start with first value
for i in range(1, len(data)):
    new_val = A * iir[i-1] + B * data[i]
    iir.append(new_val)

# FFT of filtered
iir_array = np.array(iir)
Y_iir = np.fft.fft(iir_array) / n
Y_iir = Y_iir[range(int(n/2))]

# plot
fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(t, y, 'k', label='original')
ax1.plot(t, iir, 'r', label='IIR filtered')
ax1.set_xlabel('Time [s]')
ax1.set_ylabel('Amplitude')
ax1.set_title(f'sigD - IIR filter, A={A}, B={B:.2f}')
ax1.legend()

ax2.loglog(frq, abs(Y), 'k', label='original')
ax2.loglog(frq, abs(Y_iir), 'r', label='IIR filtered')
ax2.set_xlabel('Freq (Hz)')
ax2.set_ylabel('|Y(freq)|')
ax2.set_title('FFT comparison')
ax2.legend()

plt.tight_layout()
plt.show()

#!!!!!!!!!!!!!!!!!!!!!!


#!!!!!!!!!!!!!!!!!!!!!!!

#Moving Average Filter
# X = 550  # number of points to average

# maf = []
# for i in range(len(data)):
#     if i < X:
#         maf.append(np.mean(data[0:i+1]))  # not enough points yet, average what I have
#     else:
#         maf.append(np.mean(data[i-X+1:i+1]))

# # FFT of filtered
# maf_array = np.array(maf)
# Y_maf = np.fft.fft(maf_array) / n
# Y_maf = Y_maf[range(int(n/2))]

# # plot FFT
# fig, (ax1, ax2) = plt.subplots(2, 1)
# ax1.plot(t, y, 'k', label='original')
# ax1.plot(t, maf, 'r', label='MAF filtered')
# ax1.set_xlabel('Time [s]')
# ax1.set_ylabel('Amplitude')
# ax1.set_title(f'sigD - MAF filter, X={X} points')
# ax1.legend()

# ax2.loglog(frq, abs(Y), 'k', label='original')
# ax2.loglog(frq, abs(Y_maf), 'r', label='MAF filtered')
# ax2.set_xlabel('Freq (Hz)')
# ax2.set_ylabel('|Y(freq)|')
# ax2.set_title('FFT comparison')
# ax2.legend()

# plt.tight_layout()
# plt.show() 
#!!!!!!!!!!!!!!!!!!!!!!!