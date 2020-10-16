# from server import app
# from flask import jsonify, Response,render_template
# import pyaudio
# import numpy as np
# import time
# import math
# import struct
# import matplotlib.pyplot as plt
#
# # 코드 출처: https://stackoverflow.com/questions/51079338/audio-livestreaming-with-python-flask
# # 위 코드는 server record -> client 이어서 수정해야함
# # socket 사용?
#
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 44100
# CHUNK = 1024
# RECORD_SECONDS = 5
#
# audio1 = pyaudio.PyAudio()
#
# def rms( data ):
#     count = len(data)/2
#     format = "%dh"%(count)
#     shorts = struct.unpack( format, data )
#     sum_squares = 0.0
#     for sample in shorts:
#         n = sample * (1.0/32768)
#         sum_squares += n*n
#     return math.sqrt( sum_squares / count )
#
# def genHeader(sampleRate, bitsPerSample, channels):
#     datasize = 2000*10**6
#     o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
#     o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
#     o += bytes("WAVE",'ascii')                                              # (4byte) File type
#     o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
#     o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
#     o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
#     o += (channels).to_bytes(2,'little')                                    # (2byte)
#     o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
#     o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
#     o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
#     o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
#     o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
#     o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
#     return o
#
# @app.route('/audio')
# def audio():
#     # start Recording
#     CHUNK = 1024
#     sampleRate = 44100
#     bitsPerSample = 16
#     channels = 1
#     wav_header = genHeader(sampleRate, bitsPerSample, channels)
#
#     stream = audio1.open(format=FORMAT, channels=CHANNELS,
#                     rate=RATE, input=True,
#                     frames_per_buffer=CHUNK)
#     print("recording...")
#     first_run = True
#     duration = 60
#     t_end = time.time() + duration
#
#     volume = []
#     while time.time() < t_end:
#        if first_run:
#            data = wav_header + stream.read(CHUNK)
#            first_run = False
#        else:
#            data = stream.read(CHUNK)
#        volume.append(20 * math.log10(rms(data)) + 70)
#        #yield(data)
#
#     # 0.5초당 볼륨 평균 계산
#     vol = []
#     num = 0
#     for i in range(20):
#         num += volume[i]
#     num /= 20
#     vol.append(num)
#
#     num = 0
#     for i in range(20, 40):
#         num += volume[i]
#     num /= 20
#     vol.append(num)
#
#     for i in range(duration - 1):
#         num = 0
#         for j in range(22):
#             num += volume[40 + i * 43 + j]
#         num /= 22
#         vol.append(num)
#         for j in range(22, 43):
#             num += volume[40 + i * 43 + j]
#         num /= 21
#         vol.append(num)
#
#     print(vol)
#     pitch = []
#
#     return jsonify({
#         'volume': vol,
#         'pitch': pitch
#     })
#
# @app.route('/')
# def index():
#     """Video streaming home page."""
#     return render_template('index.html')

# @app.route('/voice', methods=['POST'])
# def analyze_voice():
#     return jsonify({'main_words': main_words, 'main_sentences': main_sentences})

