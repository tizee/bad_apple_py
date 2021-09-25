import time
import convert
import curses
import signal
import threading
import sys

import fps
from frames_data import frames_data

# 30 frame per second
FRAME_RATE = 30
FRAME_HEIGHT = convert.FRAME_HEIGHT
FRAME_WIDTH = convert.FRAME_WIDTH

class Player():
    def __init__(self):
        self.min_col = -1
        self.max_col = -1
        self.min_row = -1
        self.max_row = -1
        self.running_time = 0
        # set daemon to exit thread when Ctrl-C
        self.update_time_thread=threading.Thread(target=self.update_time,daemon=True)
        self.draw_thread=threading.Thread(target=self.run_draw)
        self.stop_event=threading.Event()

        self.terminal_height = FRAME_HEIGHT
        self.terminal_width = FRAME_WIDTH


        self.winch_lock = False
        self.has_resize = False
        self.stdsrc = curses.initscr()

        self.current_frame_idx = 0

    def update_time(self):
        while True:
            self.running_time += 1
            time.sleep(1)

    def draw_loop(self):
        # self.sound_thread.run()
        timer = fps.fpstimer(FRAME_RATE)
        while not self.stop_event.isSet():
            while self.has_resize:
                pass
            # self.stdsrc.clear()
            if self.current_frame_idx >= len(frames_data):
                self.current_frame_idx = 0
            frame = frames_data[self.current_frame_idx]
            for i in range(self.min_row, self.max_row):
                # skip overflow
                if i < 0:
                    continue
                if i-self.min_row >= FRAME_HEIGHT or i >= self.terminal_height-1:
                    break
                # make sure drawing in the visible area of screen
                self.stdsrc.addstr(
                        i, max(0,self.min_col), frame[i-self.min_row][:min(self.terminal_width,self.max_col-self.min_col)], curses.color_pair(1) | curses.A_REVERSE)

            # draw time at the bottom
            time_str = f"running for {self.running_time} seconds"
            self.stdsrc.addstr(self.terminal_height-1,int(self.min_col + FRAME_WIDTH/2 - len(time_str)/2),time_str,curses.color_pair(1) | curses.A_BOLD)
            self.current_frame_idx +=1
            self.stdsrc.refresh()
            timer.sleep()

    def play(self):
        self.update_time_thread.start()

        self.terminal_height, self.terminal_width = self.stdsrc.getmaxyx()
        # center
        if self.min_col == self.max_col:
            self.min_col = int((self.terminal_width-FRAME_WIDTH) / 2)
            self.max_col = int((FRAME_WIDTH + self.terminal_width) / 2)

        if self.min_row == self.max_row:
            self.min_row = int((self.terminal_height - FRAME_HEIGHT) / 2)
            self.max_row = int((FRAME_HEIGHT + self.terminal_height) / 2)

        # make cursor invisible
        curses.curs_set(False)
        curses.start_color()
        # set up text color
        curses.init_pair(1,curses.COLOR_WHITE,curses.COLOR_BLACK)
        curses.init_pair(2,curses.COLOR_BLACK,curses.COLOR_WHITE)
        # disable echo
        curses.noecho()

        self.stdsrc.resize(self.terminal_height, self.terminal_width)

        signal.signal(signal.SIGWINCH, self.SIGWINCH_handler)
        self.draw_thread.start()
        try:
            while self.draw_thread.isAlive():
                # do nothing
                pass
        except KeyboardInterrupt:
            self.stop_event.set()
            curses.endwin()
            sys.exit(0)

    def run_draw(self):
        self.draw_loop()

    def SIGWINCH_handler(self, signum, frame):
        if self.winch_lock:
            return
        # restore to the original terminal settings
        curses.endwin()
        self.has_resize = True
        self.winch_lock = True
        # wait previous drawing to stop
        # create new screen
        self.stdsrc = curses.initscr()

        self.terminal_height, self.terminal_width = self.stdsrc.getmaxyx()

        # resize
        curses.resizeterm(self.terminal_height, self.terminal_width)
        self.stdsrc.resize(self.terminal_height, self.terminal_width)
        # center
        self.min_col = int((self.terminal_width-FRAME_WIDTH) / 2)
        self.max_col = int((FRAME_WIDTH + self.terminal_width) / 2)
        self.min_row = int((self.terminal_height - FRAME_HEIGHT) / 2)
        self.max_row = int((FRAME_HEIGHT + self.terminal_height) / 2)

        self.stdsrc.clear()
        self.stdsrc.refresh()

        self.has_resize = False
        self.winch_lock = False


if __name__ == '__main__':
    player = Player()
    player.play()
