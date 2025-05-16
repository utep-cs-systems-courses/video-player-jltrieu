#!/usr/bin/env python3

import threading
import cv2

filename = 'clip.mp4'
maxFrames = 50
inputBuffer = []
displayBuffer = []
inputSemaphore = threading.BoundedSemaphore(10)
displaySemaphore = threading.BoundedSemaphore(10)
# in this case we want to reverse how we're using the semaphores; "acquire" when we produce something
# and "release" when we consume
# it represents how many queue slots are available!
class Extractor(threading.Thread): 
    def __init__(self, videoName, outBuffer, maxFramesToLoad):
        threading.Thread.__init__(self)
        self.count = 0
        self.maxFramesToLoad = maxFramesToLoad
        self.buffer = outBuffer
        self.vidCap = cv2.VideoCapture(videoName)
    def run(self):
        print("New Extractor thread opened")

        success = True
        while success and self.count < self.maxFramesToLoad:
            success,frame = self.vidCap.read()
            #print(f'Read frame {self.count} {success}')
            self.buffer.append(frame)
            inputSemaphore.acquire()
            #print(f'input semaphore value: {inputSemaphore._value}')
            self.count += 1
        print("finished getting frames")

class Processor(threading.Thread):
    def __init__(self, inBuffer, outBuffer, maxFramesToLoad): 
        threading.Thread.__init__(self)
        self.count = 0
        self.maxFramesToLoad = maxFramesToLoad
        self.inputBuffer = inBuffer
        self.outputBuffer = outBuffer
    def run(self):
        print("New Processor thread opened")
        
        while self.count < self.maxFramesToLoad:
            #print(inputSemaphore)
            if(inputSemaphore._value < 10):
                inputSemaphore.release()
                frame = inputBuffer.pop(0)
            else:
                continue
            greyscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.outputBuffer.append(greyscale)
            displaySemaphore.acquire()
            self.count += 1
        print("finished processing frames")

class Displayer(threading.Thread):
    def __init__(self, inBuffer, maxFramesToLoad):
        threading.Thread.__init__(self)
        self.count = 0
        self.maxFramesToLoad = maxFramesToLoad
        self.buffer = inBuffer
    def run(self):
        print("New Displayer thread opened")

        while self.count < self.maxFramesToLoad:
            if(displaySemaphore._value < 10):
                displaySemaphore.release()
                frame = self.buffer.pop(0)
            else:
                continue
            cv2.imshow('look at how good i am at this', frame)
            if cv2.waitKey(42) and 0xFF == ord("q"):
                break
            self.count += 1
        print("finished displaying frames")
        cv2.destroyAllWindows()

threads = []
threads.append(Extractor(filename, inputBuffer, maxFrames))
threads.append(Processor(inputBuffer, displayBuffer, maxFrames))
threads.append(Displayer(displayBuffer, maxFrames))
for t in threads:
    t.start()
for t in threads:
    t.join()
