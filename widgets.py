import time
import sys
import select
import termios
import tty

class UiWidgets:

    def __init__(self, nameofsong):
        self.song = nameofsong
        self.current_sec = 0
        self.current_min = 0
        self.current_timeline_part = 0
        self.accumulate = 0
        self.new_timeline = "-------------------------"
        self.vinyl = ["◐","◓","◑","◒"]
        self.current_vinyl = None
        self.current_vinyl_frame = 0
        self.line_list = ["-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-","-"]

    def check_key_presses(self):
        """Checks for non-blocking keypresses."""
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)
            if key == '\x1b':
                additional = sys.stdin.read(2)
                if additional == '[C':
                    return 'RIGHT'
                elif additional == '[D':
                    return 'LEFT'
            return key
        return None

    def loop_for_song(self, player, song_time):
        # Configure terminal for raw keypress detection
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

        # Hide cursor
        print("\033[?25l", end="")

        try:
            while True:
                # 1. Read key input
                key = self.check_key_presses()
                if key:
                    if key in (' ', '\t'):  # Space / Tab = Pause/Play
                        player.pause()
                    elif key in ('d', 'RIGHT'):  # Seek forward 10s
                        pass
                    elif key in ('a', 'LEFT'):  # Seek backward 10s
                        pass
                    elif key == 'q':  # Quit
                        player.stop()
                        break

                # 2. Update state only when VLC is playing
                if player.is_playing():
                    time.sleep(1)
                    self.current_sec += 1
                    self.count()
                    self.accumulate += len(self.line_list)/song_time
                    self.change_vinyl()
                    if self.accumulate >= 1:
                        self.accumulate -= 1.0
                        self.timeline()
                    self.render(song_time)
                else:
                    time.sleep(0.1)  # Sleep briefly when paused to prevent high CPU usage

        finally:
            # Restore original terminal settings & show cursor on exit
            termios.tcsetattr(sys.stdin, termios.TCSANOW, old_settings)
            print("\033[?25h\n")

    def timeline(self):
        self.line_list[self.current_timeline_part] = "="
        self.new_timeline = "".join(self.line_list)
        self.current_timeline_part += 1

    def change_vinyl(self):
        self.current_vinyl = self.vinyl[self.current_vinyl_frame]
        if self.current_vinyl_frame < 3:
            self.current_vinyl_frame += 1
        else:
            self.current_vinyl_frame = 0

    def count(self):
        if self.current_sec >= 60:
            self.current_min += self.current_sec // 60
            self.current_sec %= 60

    def render(self, song_time):

        total_min = int(song_time // 60)
        total_sec = int(song_time % 60)

        total_time_str = f"{total_min}:{total_sec:02d}"

        lines = [
            f"[{self.new_timeline}] [{self.current_min}:{self.current_sec:02d}|{total_time_str}]",
            f"[ {self.current_vinyl} {self.song}]"
        ]

        for line in lines:
            print(f"\x1b[2K\r{line}")

        print(f"\x1b[{len(lines)}A", end="", flush=True)

