import numpy
import numpy as np
import pyaudio
import time
import librosa
from librosa import feature
import matplotlib.pyplot as plt
import pydirectinput
import controller
import keyboard
from threading import Thread

class AudioHandler(object):
    def __init__(self):
        plt.rcParams["figure.figsize"] = [7.50, 3.50]
        plt.rcParams["figure.autolayout"] = True
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024*2
        self.p = None
        self.stream = None
        self.k_controller = None
        self.thread = None

    def start(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,\
                                  channels=self.CHANNELS,\
                                  rate=self.RATE,\
                                  input=True,\
                                  output=False,\
                                  stream_callback=self.callback,\
                                  frames_per_buffer=self.CHUNK)

    def stop(self):
        self.stream.close()
        self.p.terminate()

    def GetHighestAmp(self, spectrum, freqs, start, end):
        highest_pos = 0
        highest_val = 0
        for count, val in enumerate(spectrum, start):
            if count > end:
                break

            if val > highest_val:
                highest_val = val
                highest_pos = count

        return highest_pos, highest_val, freqs[highest_pos]


    def callback(self, in_data, frame_count, time_info, flag):
        if keyboard.is_pressed('enter'):
            numpy_array = numpy.frombuffer(in_data, dtype=numpy.float32)
            fft = np.fft.fft(numpy_array)
            spectrum = np.abs(fft)
            f = np.linspace(0, self.RATE, len(spectrum))
            left_spectrum = spectrum[:int(len(spectrum) / 2)]
            left_f = f[:int(len(spectrum) / 2)]
            # for count, val in enumerate(left_f):
            #     print(f"{count} (Freq: {f[count]}): {val}")
            highest = self.GetHighestAmp(left_spectrum,left_f,0,len(left_spectrum))
            print(highest)
            self.k_controller.RegisterFreqValue(highest[0], highest[1])
            # plt.figure()
            # plt.plot(left_f, left_spectrum, alpha=0.4)
            # plt.xlabel("Frequency")
            # plt.ylabel("Magnitude")
            # plt.title("Powerspectrum")
            # plt.show()
        return None, pyaudio.paContinue

    def mainloop(self):
        while(self.stream.is_active()):
            time.sleep(2.0)


audio = AudioHandler()
f = np.linspace(0, audio.RATE, audio.CHUNK)
left_f = f[:int(audio.CHUNK / 2)]
audio.k_controller = controller.Controller(left_f)
print(audio.k_controller)
audio.k_controller.create_thread()
audio.start()
try:
    audio.mainloop()
except KeyboardInterrupt:
    print('')
finally:
    audio.stop()
    print("Stopped.")


#MAX WHISTLE 1680