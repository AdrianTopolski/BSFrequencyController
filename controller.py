import numpy as np
import pydirectinput
import operator
import time
from threading import Thread
import time

class A(object):
    def __init__(self, num):
        self.num = num

    def aa(self):
        while True:
            print(f"Snore {self.num}")
            time.sleep(1)

class Controller(object):

    def CreateKeybindMetadata(self, words):
        ret = list()
        ret.append(words[0])
        ret.append(words[1])
        if words[2] == 'p':
            ret.append("p")
        elif words[2] == 't':
            ret.append("t")
            if len(words) > 3:
                ret.append(words[3:])
            ret.append(False)
        elif words[2] == 'c':
            ret.append("c")
        ret.append(False)

        return ret

    def GetStartFreqPos(self, start_freq, freqs):
        for pos, val in enumerate(freqs):
            if val > start_freq:
                return pos


    def __init__(self, freqs):
        pydirectinput.MINIMUM_DURATION = 0.00
        pydirectinput.MINIMUM_SLEEP = 0
        pydirectinput.PAUSE = 0.00
        pydirectinput.FAILSAFE = False
        self.mouse_dir_trans = \
            {
                0: (1, 0),
                1: (0, -1),
                2: (-1, 0),
                3: (0, 1)
            }

        self.min_amplitude : float

        try:
            f_kb = open("bindings.txt", "r")
            print("Opening bindings.txt")
        except:
            print("File bindings.txt not found, creating..")
            open("bindings.txt", "x")
            f_kb = open("bindings.txt", "r")

        try:
            self.bind_dict = {}
            self.list_array = list()
            i = 0
            for line in f_kb:
                if line[0] == "\n":
                    continue
                words = line.split()
                if words[0][0] == '#':
                    continue
                if i == 0:
                    start_freq = float(words[0])
                    f_pos = self.GetStartFreqPos(start_freq, freqs)
                    self.min_amplitude = float(words[1])
                    i += 1
                    continue

                md_list = self.CreateKeybindMetadata(words)
                print(md_list)
                self.list_array.append(md_list)
                self.bind_dict[f_pos] = md_list
                f_pos -= 1
                self.bind_dict[f_pos] = md_list
                f_pos -= 1
                self.bind_dict[f_pos] = md_list
                f_pos -= 1
                i += 1

            f_kb.close()
            print(self.bind_dict)
        except Exception as error:
            f_kb.close()
            print(f"There was a problem initialising the dictionaries from bindings.txt - {error}")

    def turnoffallpress(self, cur):
        for val in self.list_array:
            if val == cur:
                continue
            if val[2] == 'p':
                if val[-1]:
                    self.release_key(val)
            elif val[2] == 'c':
                if [-1]:
                    val[-1] = False
            elif val[2] == 't':
                if val[-2]:
                    val[-2] = False


    def keypress(self, l):
        if l[2] == 'p':
            self.turnoffallpress(l)
            self.press_key(l)
        elif l[2] == 't':
            self.turnoffallpress(l)
            if l[-1]:
                if not l[-2]:
                    self.release_key(l)
                    l[-2] = True
            else:
                if not l[-2]:
                    self.press_key(l)
                    l[-2] = True
        elif l[2] == 'c':
            if not l[-1]:
                self.turnoffallpress(l)
                self.click_key(l)


    def RegisterFreqValue(self, freq_num, freq_amp):
        if freq_amp >= self.min_amplitude:
            if l := self.bind_dict.get(freq_num):
                print(f"Pressing {l}")
                self.keypress(l)
            else:
                print("Unknown frequency")
                self.turnoffallpress(None)
        else:
            print("Not Loud Enough")
            self.turnoffallpress(None)

    def click_key(self, l):
        if l[-1]:
            return
        if l[1] == 'k':
            pydirectinput.press(l[0])
            l[-1] = True
        elif l[1] == 'c':
            pydirectinput.click(button=l[0])
            l[-1] = True

    def press_key(self, l):
        if l[-1]:
            return

        if l[1] == 'k':
            pydirectinput.keyDown(l[0])
            l[-1] = True
        elif l[1] == 'm':

            l[-1] = True
        elif l[1] == 'c':
            pydirectinput.mouseDown(button=l[0])
            l[-1] = True

    def release_key(self, l):
        if not l[-1]:
            return
        if l[1] == 'k':
            pydirectinput.keyUp(l[0])
            l[-1] = False
        elif l[1] == 'm':
            l[-1] = False
        elif l[1] == 'c':
            pydirectinput.mouseUp(button=l[0])
            l[-1] = False

    def create_thread(self):
        t = Thread(target=self.run, daemon=True)
        print("Starting thread")
        t.start()
        print("Thread Started")

    def run(self):
        mouse_lists = list()
        for item in self.list_array:
            if item[1] == 'm':
                mouse_lists.append(item)

        while True:
            for i in mouse_lists:
                if i[-1]:
                    x, y = self.mouse_dir_trans[int(i[0])]
                    pydirectinput.moveRel(int(x * 8), int(y * 8), _pause=False, relative=True)
            time.sleep(0.005)
