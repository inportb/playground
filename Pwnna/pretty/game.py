#!/usr/bin/python
import curses

class Application(object):
    def __init__(self):
        pass
    
    def __call__(self, stdscr, *args, **kwargs):
        self.stdscr = stdscr
        stdscr.border()
        stdscr.addstr("Hello World.")
        while True:
            key = window.getch()
            if key == ord("q"):
                break


if __name__ == "__main__":
    app = Application()
    curses.wrapper(app)
