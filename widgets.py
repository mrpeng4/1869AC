import datetime
import importlib
import os
import random
import sys
import time
try:
    import select
except ImportError:
    select = None
try:
    import termios
    import tty
except ImportError:
    termios = None
    tty = None
if os.name == "nt":
    try:
        import msvcrt
    except ImportError:
        msvcrt = None
else:
    msvcrt = None

import vlc
from pygame import mixer

from import_system import append_folder_to_songs_path, get_playlists
import songs_path

IS_WIN = os.name == "nt"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLICK_SOUND_PATH = os.path.join(BASE_DIR, "turning_pages-ui-toggle-off-confirmation-608627.mp3")

BOX_INNER_WIDTH = 60


def _enable_vt():
    # ponytail: Win10+ only, turns on ANSI handling; no-op elsewhere
    if IS_WIN:
        os.system("")


def _song_name(path):
    # ponytail: normalize sep so basename works for mac (/) and win (\) paths
    return os.path.basename(str(path).replace("\\", "/"))


def truncate(text, max_width):
    return text if len(text) <= max_width else text[:max_width - 3] + "..."


def box_row(left, right=""):
    gap = BOX_INNER_WIDTH - len(left) - len(right)
    return "|" + left + " " * max(gap, 1) + right + "|"


class UiWidgets:

    def __init__(self, name_of_song, player):
        mixer.init()
        self.click_sound = mixer.Sound(CLICK_SOUND_PATH)
        self.song = name_of_song
        self.current_sec = 0
        self.current_min = 0
        self.new_timeline = "-" * 25

        # Spinning vinyl (original symbols)
        self.vinyl = ["◐", "◓", "◑", "◒"]
        self.current_vinyl = "◐"
        self.current_vinyl_frame = 0
        self.last_vinyl_time = time.monotonic()

        # Volume (original symbols)
        self.volume_level = 10
        self.volume_list = [" "] + ["■"] * 10 + [" "]
        player.audio_set_volume(100)

        # Modes (original symbols)
        self.play_pause = "⏸"
        self.line_list = ["-"] * 25
        self.shuffle = False
        self.shuffle_symbol = "⇉"
        self.shuffled_song_list = []
        self.loop_type = "auto"
        self.loop_type_symbol = "↬"

        self.previous_vol_lvl = 0
        self.mute_on_off = False
        self.old_settings = None

    def check_key_presses(self):
        if IS_WIN:
            if msvcrt is None or not msvcrt.kbhit():
                return None
            ch = msvcrt.getwch()
            if ch in ('\x00', '\xe0'):
                if not msvcrt.kbhit():
                    return None
                ch2 = msvcrt.getwch()
                return {'M': 'RIGHT', 'K': 'LEFT', 'H': 'UP', 'P': 'DOWN'}.get(ch2)
            return ch.lower() if ch else None

        fd = sys.stdin.fileno()
        if not select.select([fd], [], [], 0)[0]:
            return None

        key = os.read(fd, 1).decode(errors="ignore")
        if key == '\x1b':
            if select.select([fd], [], [], 0.02)[0]:
                seq = os.read(fd, 2).decode(errors="ignore")
                return {'[C': 'RIGHT', '[D': 'LEFT', 'OC': 'RIGHT', 'OD': 'LEFT',
                        '[A': 'UP', '[B': 'DOWN', 'OA': 'UP', 'OB': 'DOWN'}.get(seq)
            return None
        return key.lower() if key else None

    def loop_for_song(self, player, song_time, playlist, current_index):
        if IS_WIN:
            self.old_settings = None
            _enable_vt()
        else:
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
        print("\033[?25l", end="")
        self.clear_screen()

        consecutive_errors = 0

        try:
            while True:
                self.now_real_time = datetime.datetime.now().strftime("%d %b %Y %I:%M %p")
                key = self.check_key_presses()

                if key:
                    if key in (' ', 'k'):
                        self.click_sound.play()
                        state = player.get_state()
                        if state == vlc.State.Paused:
                            player.set_pause(0)
                        elif state == vlc.State.Playing:
                            player.set_pause(1)
                        else:
                            player.play()

                    elif key in ('d', 'l', 'RIGHT'):
                        self.click_sound.play()
                        new_ms = min(max(player.get_time(), 0) + 10000, int(song_time * 1000))
                        player.set_time(new_ms)
                        self.sync_timeline(song_time, new_ms)

                    elif key in ('a', 'j', 'LEFT'):
                        self.click_sound.play()
                        new_ms = max(player.get_time() - 10000, 0)
                        player.set_time(new_ms)
                        self.sync_timeline(song_time, new_ms)

                    elif key == 'p':
                        if self.volume_level < 10:
                            self.click_sound.play()
                            self.set_volume(player, self.volume_level + 1)

                    elif key == 'o':
                        if self.volume_level > 0:
                            self.click_sound.play()
                            self.set_volume(player, self.volume_level - 1)

                    elif key == 's':
                        self.click_sound.play()
                        self.shuffle = not self.shuffle
                        self.shuffle_symbol = "⤭" if self.shuffle else "⇉"

                    elif key == 'e':
                        self.click_sound.play()
                        self.loop_type = "one" if self.loop_type == "auto" else "auto"
                        self.loop_type_symbol = "⥁" if self.loop_type == "one" else "↬"

                    elif key == 'm':
                        player, song_time, current_index = self.next_song(
                            player, playlist, current_index, self.shuffle)

                    elif key == 'n':
                        player, song_time, current_index = self.previous_song(
                            player, playlist, current_index, self.shuffle)

                    elif key == 'q':
                        self.click_sound.play()
                        self.play_pause = "▶"
                        self.render(song_time)
                        break

                    elif key == '0':
                        self.click_sound.play()
                        if self.mute_on_off:
                            self.set_volume(player, self.previous_vol_lvl)
                        elif self.volume_level > 0:
                            self.previous_vol_lvl = self.volume_level
                            self.set_volume(player, 0)
                            self.mute_on_off = True

                    elif key == 'c':
                        was_paused = player.get_state() == vlc.State.Paused
                        player.set_pause(1)
                        self.click_sound.play()
                        self.import_songs_prompt()
                        if not was_paused:
                            player.set_pause(0)

                    elif key == 'x':
                        was_paused = player.get_state() == vlc.State.Paused
                        player.set_pause(1)
                        self.click_sound.play()
                        old_player = player
                        player, song_time, playlist, current_index = self.select_playlist(
                            player, playlist, song_time, current_index)
                        if player is old_player and not was_paused:
                            player.set_pause(0)

                    elif key == 'z':
                        was_paused = player.get_state() == vlc.State.Paused
                        player.set_pause(1)
                        self.click_sound.play()
                        old_player = player
                        player, song_time, playlist, current_index = self.select_songs(
                            player, playlist, song_time, current_index)
                        if player is old_player and not was_paused:
                            player.set_pause(0)

                if song_time <= 1:
                    length = player.get_length()
                    if length > 0:
                        song_time = length / 1000

                state = player.get_state()
                self.play_pause = "▶" if state == vlc.State.Paused else "⏸"

                if player.is_playing():
                    consecutive_errors = 0
                    self.sync_timeline(song_time, max(0, player.get_time()))

                    now = time.monotonic()
                    if now - self.last_vinyl_time >= 0.3:
                        self.change_vinyl()
                        self.last_vinyl_time = now

                self.render(song_time)

                state = player.get_state()
                if state == vlc.State.Error:
                    consecutive_errors += 1
                    if consecutive_errors >= len(playlist):
                        self.clear_screen()
                        print("None of the songs in this playlist could be played.")
                        break
                    player, song_time, current_index = self.next_song(
                        player, playlist, current_index, self.shuffle)
                elif state == vlc.State.Ended:
                    if self.loop_type == "one":
                        player, song_time, current_index = self.loop(player, playlist, current_index)
                    else:
                        player, song_time, current_index = self.next_song(
                            player, playlist, current_index, self.shuffle)

                time.sleep(0.1)

        finally:
            try:
                player.stop()
            except Exception:
                pass
            if not IS_WIN and self.old_settings is not None:
                termios.tcsetattr(sys.stdin, termios.TCSANOW, self.old_settings)
            print("\033[?25h\n")

    def clear_screen(self):
        # ponytail: native cls on win (VT-independent); ANSI + scrollback wipe elsewhere
        if IS_WIN:
            os.system("cls")
        else:
            print("\033[3J\033[H\033[2J", end="", flush=True)

    def set_volume(self, player, level):
        self.volume_level = level
        self.mute_on_off = False
        self.update_volume_bar()
        player.audio_set_volume(level * 10)

    def sync_timeline(self, song_time, current_ms):
        current_sec = max(0, min(current_ms / 1000, song_time))
        self.current_min = int(current_sec // 60)
        self.current_sec = int(current_sec % 60)

        progress_ratio = current_sec / song_time if song_time > 0 else 0
        filled_units = int(progress_ratio * len(self.line_list))
        self.line_list = ["="] * filled_units + ["-"] * (len(self.line_list) - filled_units)
        self.new_timeline = "".join(self.line_list)

    def change_vinyl(self):
        self.current_vinyl_frame = (self.current_vinyl_frame + 1) % len(self.vinyl)
        self.current_vinyl = self.vinyl[self.current_vinyl_frame]

    def update_volume_bar(self):
        # ponytail: 12-slot field, left-aligned fills, padded space on both sides at any level
        self.volume_list = [" "] + ["■"] * self.volume_level + [" "] * (11 - self.volume_level)

    def _start_player(self, path):
        new_player = vlc.MediaPlayer(path)
        new_player.audio_set_volume(self.volume_level * 10)
        new_player.play()

        retries = 0
        while new_player.get_length() <= 0 and retries < 100:
            if new_player.get_state() in (vlc.State.Error, vlc.State.Ended):
                break
            time.sleep(0.1)
            retries += 1

        new_player.audio_set_volume(self.volume_level * 10)
        return new_player, max(new_player.get_length() / 1000, 1)

    def _dispose(self, player):
        try:
            player.stop()
            player.release()
        except Exception:
            pass

    def import_songs_prompt(self):
        self.disable_cbreak(self.old_settings)
        self.clear_screen()
        print("--- IMPORT PLAYLIST ---", flush=True)

        print("Please paste folder path where music is located: ")
        user_directory = input().strip()
        print("Please provide a name for the playlist: ")
        user_playlist_name = input().strip()

        if user_directory and user_playlist_name:
            append_folder_to_songs_path(user_directory, user_playlist_name)
        time.sleep(1.5)
        self.clear_screen()
        self.enable_cbreak()

    def select_playlist(self, player, playlist, song_time, current_index):
        self.disable_cbreak(self.old_settings)
        self.clear_screen()

        try:
            importlib.reload(songs_path)
        except Exception as e:
            print(f"Could not read songs_path.py: {e}")
            time.sleep(1.5)
            self.clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        playlists = get_playlists()

        if not playlists:
            print("No playlists found. Press C to import one.")
            time.sleep(1.5)
            self.clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        names = list(playlists)

        print("\n         SELECT A PLAYLIST          \n")
        for index, name in enumerate(names):
            tag = "" if any(os.path.isfile(s) for s in playlists[name]) else "  [missing]"
            print(f"{index}. {name}{tag}")

        print("Enter number: ", end="", flush=True)
        playlist_index = input().strip()

        if not playlist_index.isdigit() or int(playlist_index) >= len(names):
            print("Invalid selection. Returning to player...")
            time.sleep(1)
            self.clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        new_playlist = playlists[names[int(playlist_index)]]
        if not new_playlist or not any(os.path.isfile(s) for s in new_playlist):
            print(f"Playlist '{names[int(playlist_index)]}' has no files on this computer.")
            time.sleep(1.5)
            self.clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        self._dispose(player)
        self.shuffled_song_list.clear()

        current_song = new_playlist[0]

        new_player, new_song_time = self._start_player(current_song)
        self.reset(_song_name(current_song))

        self.clear_screen()
        self.enable_cbreak()

        return new_player, new_song_time, new_playlist, 0

    def select_songs(self, player, playlist, song_time, current_index):
        self.clear_screen()

        start = 0
        end = 10
        select_index = 0
        temp_select_list = [_song_name(song) for song in playlist]
        needs_redraw = True

        while True:
            total = len(temp_select_list)
            start = max(0, min(start, max(0, total - 10)))
            end = min(start + 10, total)

            if needs_redraw:
                out = "\033[H"
                for line_index in range(start, end):
                    song_name = temp_select_list[line_index]
                    if line_index == select_index:
                        out += f"\033[2K\r> {song_name} <\n"
                    else:
                        out += f"\033[2K\r  {song_name}  \n"
                out += "\033[2K\r   [Up/N] Up | [Down/M] Down | [Enter] Play | [Q] Back\n"
                out += "\033[J"
                sys.stdout.write(out)
                sys.stdout.flush()
                needs_redraw = False

            key = self.check_key_presses()

            if key == 'q':
                break

            if key in ('m', 'DOWN'):
                if select_index < len(temp_select_list) - 1:
                    select_index += 1
                    needs_redraw = True
                    if start < len(temp_select_list) - 10 and select_index > start:
                        start += 1
                        end += 1

            if key in ('n', 'UP'):
                if select_index > 0:
                    select_index -= 1
                    needs_redraw = True
                    if select_index < start:
                        start -= 1
                        end -= 1

            if key and len(key) == 1 and ord(key) in (10, 13):
                self._dispose(player)
                self.click_sound.play()

                selected_song_path = playlist[select_index]
                new_song_name = temp_select_list[select_index]

                new_player, new_song_time = self._start_player(selected_song_path)
                self.reset(new_song_name)

                self.clear_screen()
                return new_player, new_song_time, playlist, select_index

            time.sleep(0.05)

        self.clear_screen()
        return player, song_time, playlist, current_index

    def render(self, song_time):
        total_min = int(song_time // 60)
        total_sec = int(song_time % 60)
        total_time_str = f"{total_min:02d}:{total_sec:02d}"
        curr_time_str = f"{self.current_min:02d}:{self.current_sec:02d}"

        display_name = truncate(self.song, 28)
        border = "+" + "-" * BOX_INNER_WIDTH + "+"

        lines = [
            border,
            box_row("  AUDIO DECK", f"{self.now_real_time}  "),
            box_row(f"  Track: {display_name}", f"Vinyl: [{self.current_vinyl}]  "),
            box_row(f"  [{self.new_timeline}]", f"{curr_time_str} / {total_time_str}  "),
            box_row(f"  Vol:   [{''.join(self.volume_list)}]  {self.volume_level * 10:>3}%",
                    f"Mode: [ {self.loop_type_symbol} {self.play_pause} {self.shuffle_symbol} ]  "),
            border,
            "   [Space] Play/Pause | [M] Next | [N] Prev | [X] List | [Q] Quit",
            "   [A/D] Seek | [O/P] Volume | [0] Mute | [S] Shuffle | [E] Repeat | [C] Import | [Z] Songs",
        ]

        out = "\033[H" + "".join(f"\033[2K\r{line}\n" for line in lines) + "\033[J"
        sys.stdout.write(out)
        sys.stdout.flush()

    def reset(self, song_name):
        self.clear_screen()
        self.song = song_name
        self.current_sec = 0
        self.current_min = 0
        self.new_timeline = "-" * 25
        self.line_list = ["-"] * 25
        self.play_pause = "⏸"
        self.last_vinyl_time = time.monotonic()

    def disable_cbreak(self, old_settings):
        if IS_WIN:
            print("\033[?25h", end="", flush=True)
            return
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        termios.tcsetattr(sys.stdin, termios.TCSANOW, old_settings)
        print("\033[?25h", end="", flush=True)

    def enable_cbreak(self):
        if IS_WIN:
            print("\033[?25l", end="", flush=True)
            return
        tty.setcbreak(sys.stdin.fileno())
        print("\033[?25l", end="", flush=True)
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

    def next_song(self, player, playlist, current_index, shuffle):
        if shuffle:
            self.shuffled_song_list.append(current_index)
            del self.shuffled_song_list[:-200]
            next_index = random.randrange(len(playlist))
            while len(playlist) > 1 and next_index == current_index:
                next_index = random.randrange(len(playlist))
        else:
            next_index = (current_index + 1) % len(playlist)

        self._dispose(player)
        self.click_sound.play()

        next_song_path = playlist[next_index]
        new_player, new_song_time = self._start_player(next_song_path)
        self.reset(_song_name(next_song_path))
        return new_player, new_song_time, next_index

    def previous_song(self, player, playlist, current_index, shuffle):
        if shuffle and self.shuffled_song_list:
            previous_index = self.shuffled_song_list.pop() % len(playlist)
        else:
            previous_index = (current_index - 1) % len(playlist)

        self._dispose(player)
        self.click_sound.play()

        previous_song_path = playlist[previous_index]
        new_player, new_song_time = self._start_player(previous_song_path)
        self.reset(_song_name(previous_song_path))
        return new_player, new_song_time, previous_index

    def loop(self, player, playlist, current_index):
        self._dispose(player)
        self.click_sound.play()

        current_song_path = playlist[current_index]
        new_player, new_song_time = self._start_player(current_song_path)
        self.reset(_song_name(current_song_path))
        return new_player, new_song_time, current_index
