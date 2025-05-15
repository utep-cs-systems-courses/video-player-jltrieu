#!/usr/bin/env python3

import threading
import cv2

maxFrames = 50
inputBuffer = []
displayBuffer = []
inputSemaphore = threading.Semaphore(1)
displaySemaphore = threading.Semaphore(1)

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
            inputSemaphore.release()
            self.count += 1
        print("finished getting frames")

filename = 'clip.mp4'

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
            with inputSemaphore:
                inputSemaphore.acquire()
                frame = inputBuffer.pop(0)
            greyscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.outputBuffer.append(greyscale)
            displaySemaphore.release()
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
            with displaySemaphore:
                displaySemaphore.acquire()
                frame = self.buffer.pop(0)
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
