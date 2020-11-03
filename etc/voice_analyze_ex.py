import pyaudio
import time
import numpy as np
import math
import matplotlib.pyplot as plt
import struct

def rms( data ):
    count = len(data)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, data )
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n*n
    return math.sqrt( sum_squares / count )


CHUNK = 1024
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=CHUNK)

# 1초에 40 2초부터 43씩
duration = 60
t_end = time.time() + duration
volume = []
while time.time() < t_end:
    data = rms(stream.read(CHUNK))
    volume.append(20 * math.log10(data)+70)

print(len(volume))
stream.stop_stream()
stream.close()
p.terminate()

vol = []
num = 0
for i in range(20):
    num += volume[i]
num /= 20
vol.append(num)

num = 0
for i in range(20,40):
    num += volume[i]
num /= 20
vol.append(num)


for i in range(duration-1):
    num = 0
    for j in range(22):
        num += volume[40+i*43+j]
    num /= 22
    vol.append(num)
    for j in range(22,43):
        num += volume[40+i*43+j]
    num /= 21
    vol.append(num)

print(len(vol))

s = vol
t = np.arange(0, len(s)/2, 0.5)

fig, ax = plt.subplots()
ax.plot(t,s)
plt.show()