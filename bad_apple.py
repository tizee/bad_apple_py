from frames_data import frames_data
import time
import convert
import curses
import signal
import playsound
import threading

# 60 frame per second
FRAME_RATE = 1 / 30
FRAME_HEIGHT = convert.FRAME_HEIGHT
FRAME_WIDTH = convert.FRAME_WIDTH


def play_mp3(sound="bad_apple.mp3"):
    playsound.playsound(sound, False)

class Player():
    def __init__(self):
        self.min_col = -1
        self.max_col = -1
        self.min_row = -1
        self.max_row = -1
        # self.sound_thread=threading.Thread(target=play_mp3)

        self.terminal_height = FRAME_HEIGHT
        self.terminal_width = FRAME_WIDTH
        self.winch_lock = False

        self.has_resize = False
        self.stdsrc = curses.initscr()

    def draw_loop(self):
        # self.sound_thread.run()
        now = time.time()
        count = 0
        while True:
            for idx in range(len(frames_data)):
                for i in range(self.min_row, self.max_row):
                    if i < 0:
                        continue
                    if i-self.min_row >= FRAME_HEIGHT or i >= self.terminal_height:
                        break
                    try:
                        self.stdsrc.addstr(
                            i, self.min_col, frames_data[idx][i-self.min_row], curses.COLOR_WHITE)
                    except Exception as e:
                        print(
                            i-self.min_row, len(frames_data[idx]), FRAME_HEIGHT, self.terminal_height)
                        raise e
                if self.has_resize:
                    break
                # throttle speed
                while time.time() - now < (count * FRAME_RATE):
                    time.sleep(count*FRAME_RATE-time.time()+now)
                self.stdsrc.refresh()
                count += 1
            if self.has_resize:
                break

    def play(self):
        self.terminal_height, self.terminal_width = self.stdsrc.getmaxyx()
        if self.min_col == self.max_col:
            self.min_col = int((self.terminal_width-FRAME_WIDTH) / 2)
            self.max_col = int((FRAME_WIDTH + self.terminal_width) / 2)

        if self.min_row == self.max_row:
            self.min_row = int((self.terminal_height - FRAME_HEIGHT) / 2)
            self.max_row = int((FRAME_HEIGHT + self.terminal_height) / 2)
        curses.start_color()
        self.stdsrc.resize(self.terminal_height, self.terminal_width)
        signal.signal(signal.SIGWINCH, self.SIGWINCH_handler)
        self.draw_loop()

    def SIGWINCH_handler(self, signum, frame):
        if self.winch_lock:
            return
        curses.endwin()
        self.has_resize = True
        self.winch_lock = True
        # wait previous drawing to stop
        time.sleep(0.1)
        self.stdsrc = curses.initscr()
        self.terminal_height, self.terminal_width = self.stdsrc.getmaxyx()
        curses.resizeterm(self.terminal_height, self.terminal_width)
        self.stdsrc.resize(self.terminal_height, self.terminal_width)
        self.min_col = int((self.terminal_width-FRAME_WIDTH) / 2)
        self.max_col = int((FRAME_WIDTH + self.terminal_width) / 2)
        self.min_row = int((self.terminal_height - FRAME_HEIGHT) / 2)
        self.max_row = int((FRAME_HEIGHT + self.terminal_height) / 2)
        self.stdsrc.clear()
        self.stdsrc.refresh()
        self.has_resize = False
        self.winch_lock = False
        self.draw_loop()


if __name__ == '__main__':
    player = Player()
    player.play()
