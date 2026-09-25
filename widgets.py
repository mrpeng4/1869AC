import time
import sys
import select
import termios
import tty
import vlc

class UiWidgets:

    def __init__(self, name_of_song):
        self.song = name_of_song
        self.current_sec = 0
        self.current_min = 0
        self.current_timeline_part = 0
        self.accumulate = 0
        self.seconds_for_vinyl = 0
        self.new_timeline = "-------------------------"
        self.vinyl = ["◐", "◓", "◑", "◒"]
        self.play_pause = "⏸"
        self.current_vinyl = "◐"
        self.current_vinyl_frame = 0
        self.line_list = ["-"] * 25

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

        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        print("\033[?25l", end="")

        try:
            while True:
                self.play_pause = "⏸"
                key = self.check_key_presses()
                if key:

                    if key in (' ',"k"):
                        self.play_pause = "▶"# Space = Pause/Play
                        player.pause()

                    elif key in ('d',"l"):  # Seek forward 10s
                        new_ms = min(player.get_time() + 10000, int(song_time * 1000))
                        player.set_time(new_ms)
                        self.sync_timeline(song_time, new_ms)

                    elif key in ('a',"j"):  # Seek backward 10s
                        new_ms = max(player.get_time() - 10000, 0)
                        player.set_time(new_ms)
                        self.sync_timeline(song_time, new_ms)

                    elif key == 'q':  # Quit
                        player.stop()
                        self.play_pause = "▶"
                        self.render(song_time)
                        break

                if player.is_playing():
                    time.sleep(0.1)
                    current_ms = max(0, player.get_time())
                    total_sec = int(current_ms / 1000)
                    self.current_min = int(total_sec / 60)
                    self.current_sec = total_sec % 60
                    self.sync_timeline(song_time, current_ms)
                    self.seconds_for_vinyl += 0.1
                    if self.seconds_for_vinyl >= 1.0:
                        self.change_vinyl()
                        self.seconds_for_vinyl = 0
                    self.render(song_time)
                else:
                    time.sleep(0.1)
                if player.get_state() == vlc.State.Ended:
                    self.new_timeline = "========================="
                    self.play_pause = "▶"
                    self.render(song_time)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSANOW, old_settings)
            print("\033[?25h\n")

    def sync_timeline(self, song_time, current_ms):
        current_sec = max(0, min(current_ms / 1000, song_time))
        progress_ratio = current_sec / song_time if song_time > 0 else 0

        total_units = progress_ratio * len(self.line_list)
        filled_units = int(total_units)

        self.current_timeline_part = filled_units
        self.accumulate = total_units - filled_units
        self.line_list = ["="] * filled_units + ["-"] * (len(self.line_list) - filled_units)
        self.new_timeline = "".join(self.line_list)

    def change_vinyl(self):
        self.current_vinyl = self.vinyl[self.current_vinyl_frame]
        if self.current_vinyl_frame < 3:
            self.current_vinyl_frame += 1
        else:
            self.current_vinyl_frame = 0

    def render(self, song_time):
        total_min = int(song_time // 60)
        total_sec = int(song_time % 60)
        total_time_str = f"{total_min}:{total_sec:02d}"
        lines = [
            f"[{self.new_timeline}] [{self.current_min}:{self.current_sec:02d}|{total_time_str}] [ ⏮  {self.play_pause} ⏭ ]",
            f"[ {self.current_vinyl} {self.song}]"
        ]
        for line in lines:
            print(f"\x1b[2K\r{line}")
        print(f"\x1b[{len(lines)}A", end="", flush=True)

    def next_song(self):
        pass

