import time
import sys
import os
import platform
import vlc
import datetime
from pygame import mixer
import random
from import_system import append_folder_to_songs_path
import songs_path

###########
platforms = 'mac'
if platform.system() == "Windows":
    import msvcrt
    platforms = 'windows'
else:
    import select
    import termios 
    import tty
    platforms = 'mac'

class UiWidgets:

    def __init__(self, name_of_song, player):
        mixer.init()
        self.click_sound = mixer.Sound("./turning_pages-ui-toggle-off-confirmation-608627.mp3")
        self.song = name_of_song
        self.current_sec = 0
        self.current_min = 0
        self.current_timeline_part = 0
        self.seconds_for_vinyl = 0
        self.new_timeline = "-------------------------"
        self.vinyl = ["◐", "◓", "◑", "◒"]
        self.volume_level = 10
        self.volume_list = ["⏹"] * 10
        player.audio_set_volume(100)
        self.play_pause = "⏸"
        self.current_vinyl = "◐"
        self.current_vinyl_frame = 0
        self.line_list = ["-"] * 25
        self.shuffle = False
        self.shuffle_symbol = "⇉"
        self.shuffled_song_list = []
        self.loop_type = "auto"
        self.loop_type_symbol = "↬"
        self.previous_vol_lvl = 0
        self.mute_on_off = False
        self.playlist_added = False
        self.old_settings = None

    def check_key_presses(self):
        if platforms == "windows":
            if msvcrt.kbhit(): #press
                key = msvcrt.getch()
                if key == b'\xe0' or key == b'\x00': #bytes not string
                    additional = msvcrt.getch()
                    if additional == b'M':
                        return 'RIGHT'
                    elif additional == b'K': #special for arrow keys
                        return 'LEFT'
                #normal keys
                try:
                    return key.decode("utf-8")
                except UnicodeDecodeError:
                    return None
        else:
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

    def loop_for_song(self, player, song_time, playlist, current_index):
        if platforms == "windows":
            os.system('') #enabling the escape sequences for older windows 
            while msvcrt.kbhit():
                msvcrt.getch() #read
            print("\033[?25l", end="")
            self.old_settings = None
        else:
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
            print("\033[?25l", end="")

        try:
            while True:
                self.now_real_time = datetime.datetime.now().strftime("%d %b %Y %I:%M")
                self.play_pause = "⏸"
                key = self.check_key_presses()

                if key:
                    if key in (' ',"k"):
                        self.play_pause = "▶"
                        self.click_sound.play()
                        player.pause()

                    elif key in ('d',"l"):
                        self.click_sound.play()
                        new_ms = min(player.get_time() + 10000, int(song_time * 1000))
                        player.set_time(new_ms)
                        self.sync_timeline(song_time, new_ms)

                    elif key in ('a',"j"):
                        self.click_sound.play()
                        new_ms = max(player.get_time() - 10000, 0)
                        player.set_time(new_ms)
                        self.sync_timeline(song_time, new_ms)

                    elif key == "p":
                        if self.volume_level < 10:
                            self.click_sound.play()
                            self.volume_level += 1
                            self.update_volume_bar()
                            player.audio_set_volume(self.volume_level * 10)

                    elif key == "o":
                        if self.volume_level > 0:
                            self.click_sound.play()
                            self.volume_level -= 1
                            self.update_volume_bar()
                            player.audio_set_volume(self.volume_level * 10)

                    elif key == "s":
                        self.click_sound.play()
                        if self.shuffle:
                            self.shuffle = False
                            self.shuffle_symbol = "⇉"
                        else:
                            self.shuffle = True
                            self.shuffle_symbol = "⤭"

                    elif key == "e":
                        self.click_sound.play()
                        if self.loop_type == "one":
                            self.loop_type = "auto"
                            self.loop_type_symbol = "↬"
                        else:
                            self.loop_type = "one"
                            self.loop_type_symbol = "⥁"

                    elif key == "m":
                        player, song_time, current_index = self.next_song(player, playlist, current_index, self.shuffle)

                    elif key == "n":
                        player, song_time, current_index = self.previous_song(player, playlist, current_index, self.shuffle)

                    elif key == 'q':  # Quit
                        player.stop()
                        self.click_sound.play()
                        self.play_pause = "▶"
                        self.render(song_time)
                        break

                    elif key == '0':
                        if not self.mute_on_off:
                            self.click_sound.play()
                            self.previous_vol_lvl = self.volume_level
                            self.volume_level = 0
                            self.update_volume_bar()
                            player.audio_set_volume(self.volume_level * 10)
                            self.mute_on_off = True
                        else:
                            self.click_sound.play()
                            self.volume_level = self.previous_vol_lvl
                            self.update_volume_bar()
                            player.audio_set_volume(self.volume_level * 10)
                            self.mute_on_off = False

                    elif key == "c":
                        player.pause()
                        self.click_sound.play()
                        self.import_songs_prompt()
                        player.play()
                        self.play_pause = "⏸"

                    elif key == "x":
                        player.pause()
                        self.click_sound.play()
                        player, song_time, playlist, current_index = self.select_playlist(player, playlist, song_time, current_index)
                        player.play()
                        self.play_pause = "⏸"

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
                    if self.loop_type == "one":
                        player, song_time, current_index = self.loop(player, playlist, current_index)
                    else:
                        player, song_time, current_index = self.next_song(player, playlist, current_index, self.shuffle)
        finally:
            if platforms == "windows":
                print("\033[?25h\n")
            else:
                termios.tcsetattr(sys.stdin, termios.TCSANOW, self.old_settings)
                print("\033[?25h\n")

    def sync_timeline(self, song_time, current_ms):
        current_sec = max(0, min(current_ms / 1000, song_time))
        progress_ratio = current_sec / song_time if song_time > 0 else 0

        total_units = progress_ratio * len(self.line_list)
        filled_units = int(total_units)

        self.current_timeline_part = filled_units
        self.line_list = ["="] * filled_units + ["-"] * (len(self.line_list) - filled_units)
        self.new_timeline = "".join(self.line_list)

    def change_vinyl(self):
        self.current_vinyl = self.vinyl[self.current_vinyl_frame]
        if self.current_vinyl_frame < 3:
            self.current_vinyl_frame += 1
        else:
            self.current_vinyl_frame = 0

    def import_songs_prompt(self):
        self.disable_cbreak(self.old_settings)
        print("\033[H\033[2J", end="", flush=True)
        print("--- IMPORT PLAYLIST ---", flush=True)

        print("Please paste folder path where music is located: ", end="", flush=True)
        user_directory = input().strip()
        print("Please provide a name for the playlist: ", end="", flush=True)
        user_playlist_name = input().strip()

        if user_directory and user_playlist_name:
            self.playlist_added = append_folder_to_songs_path(user_directory, user_playlist_name)
        time.sleep(1)
        print("\033[H\033[2J", end="", flush=True)
        self.enable_cbreak()

    def render(self, song_time):
        print("\033[3J\033[H\033[2J", end="", flush=True)

        total_min = int(song_time // 60)
        total_sec = int(song_time % 60)
        total_time_str = f"{total_min}:{total_sec:02d}"

        lines = [
            f"[{self.new_timeline}] [{self.current_min}:{self.current_sec:02d}|{total_time_str}] [ {self.loop_type_symbol} {self.play_pause} {self.shuffle_symbol} ] [{''.join(self.volume_list)}]",
            f"[ {self.current_vinyl} {self.song}] [{self.now_real_time}]"
        ]

        for line in lines:
            print(f"\x1b[2K\r{line}")
        print(f"\x1b[{len(lines)}A", end="", flush=True)

    def reset(self, song_name):
        self.song = song_name
        self.current_sec = 0
        self.current_min = 0
        self.current_timeline_part = 0
        self.seconds_for_vinyl = 0
        self.new_timeline = "-------------------------"
        self.line_list = ["-"] * 25
        self.play_pause = "⏸"

    def disable_cbreak(self, old_settings):
        if platforms == "windows":
            os.system('') #enabling the escape sequences for older windows 
            while msvcrt.kbhit():
                msvcrt.getch() #read
            print("\033[?25h", end="", flush=True)
        else:
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
            termios.tcsetattr(sys.stdin, termios.TCSANOW, old_settings)
            print("\033[?25h", end="", flush=True)

    def enable_cbreak(self):
        if platforms == "windows":
             os.system('') #enabling the escape sequences for older windows 
             while msvcrt.kbhit():
                msvcrt.getch() #read
        else:
            tty.setcbreak(sys.stdin.fileno())
            print("\033[?25l", end="", flush=True)
            termios.tcflush(sys.stdin, termios.TCIFLUSH)

    def select_playlist(self, player, playlist, song_time, current_index):
        self.disable_cbreak(self.old_settings)
        print("\033[H\033[2J", end="", flush=True)

        playlists_list = []

        for variable_name in dir(songs_path):
            if not variable_name.startswith("__"):
                playlists_list.append(variable_name)

        print(" ")
        print("         SELECT A PLAYLIST          ")
        print(" ")

        for index in range(0, len(playlists_list)):
            print(f"{index}. {playlists_list[index]}")

        playlist_index = input("").strip()

        if not playlist_index.isdigit() or int(playlist_index) >= len(playlists_list):
            print("Invalid selection. Returning to player...")
            time.sleep(1)
            print("\033[H\033[2J", end="", flush=True)
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        player.stop()

        name_for_Playlist = playlists_list[int(playlist_index)]
        new_playlist = getattr(songs_path, name_for_Playlist)
        current_song_index = 0
        current_song = new_playlist[current_song_index]

        new_song_name = os.path.basename(current_song)
        new_player = vlc.MediaPlayer(current_song)

        new_player.audio_set_volume(self.volume_level * 10)
        new_player.play()

        while new_player.get_length() <= 0:
            time.sleep(0.1)

        new_song_time = new_player.get_length() / 1000
        self.reset(new_song_name)

        print("\033[H\033[2J", end="", flush=True)
        self.enable_cbreak()

        return new_player, new_song_time, new_playlist, 0

    def select_songs(self):
        pass

    def next_song(self, player, playlist, current_index, shuffle):
        if shuffle:
            self.shuffled_song_list.append(current_index)
            next_index = random.randint(0, len(playlist) - 1)
        else:
            next_index = (current_index + 1) % len(playlist)

        player.stop()
        self.click_sound.play()
        next_song_path = playlist[next_index]

        next_song_name = os.path.basename(next_song_path) #windiws \ vs mac /

        new_player = vlc.MediaPlayer(next_song_path)
        new_player.audio_set_volume(self.volume_level * 10)
        new_player.play()

        while new_player.get_length() <= 0:
            time.sleep(0.1)

        new_song_time = new_player.get_length() / 1000
        self.reset(next_song_name)

        return new_player, new_song_time, next_index

    def previous_song(self, player, playlist, current_index, shuffle):
        if shuffle:
            if self.shuffled_song_list != []:
                previous_index = self.shuffled_song_list.pop(-1)
            else:
                previous_index = (current_index - 1) % len(playlist)
        else:
            previous_index = (current_index - 1) % len(playlist)
        player.stop()
        self.click_sound.play()
        previous_song_path = playlist[previous_index]

        previous_song_name = os.path.basename(previous_song_path)

        new_player = vlc.MediaPlayer(previous_song_path)
        new_player.audio_set_volume(self.volume_level * 10)
        new_player.play()

        while new_player.get_length() <= 0:
            time.sleep(0.1)

        new_song_time = new_player.get_length() / 1000
        self.reset(previous_song_name)

        return new_player, new_song_time, previous_index

    def loop(self, player, playlist, current_index):
        player.stop()
        self.click_sound.play()
        current_song_path = playlist[current_index]
 
        current_song_name = os.path.basename(current_song_path)

        new_player = vlc.MediaPlayer(current_song_path)
        new_player.audio_set_volume(self.volume_level * 10)
        new_player.play()

        while new_player.get_length() <= 0:
            time.sleep(0.1)

        new_song_time = new_player.get_length() / 1000
        self.reset(current_song_name)

        return new_player, new_song_time, current_index

    def update_volume_bar(self):
        self.volume_list = ["⏹"] * self.volume_level + [" "] * (10 - self.volume_level)
