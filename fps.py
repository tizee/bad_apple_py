import time

class fpstimer():
    def __init__(self, fps):
        if fps <= 0:
            raise ValueError("fps cannot be 0")
        self.__fps = fps
        self.__secondPerFrame = 1/fps
        self.__last_count = 0
        self.__now = time.time()
        self.__last = self.__now
        self.__count = 1

    def fps(self):
        return self.__fps

    def sleep(self):
        stop = self.__count*self.__secondPerFrame-time.time()+self.__last
        # wait for too long just skip it
        if stop < 0:
            self.__now = time.time()
            self.__last = self.__now
            self.__count = 1
            return 0
        # pause
        time.sleep(stop)
        self.__now = time.time()
        self.__count += 1
        return stop
