import time
import sys
import select
import termios
import tty
import vlc
import datetime
from pygame import mixer
import random
from import_system import append_folder_to_songs_path
import songs_path
import json

class UiWidgets:

    def __init__(self, name_of_song, player, name_of_playlist, current_index, volume):
        mixer.init()

        with open("last_played.json", "r") as user_saves_raw:
            user_saves = json.load(user_saves_raw)

        self.click_sound = mixer.Sound("./turning_pages-ui-toggle-off-confirmation-608627.mp3")
        self.song = name_of_song
        self.current_sec = 0
        self.current_min = 0
        self.current_timeline_part = 0
        self.seconds_for_vinyl = 0
        self.new_timeline = "-------------------------"
        self.vinyl = ["◐", "◓", "◑", "◒"]
        self.volume_level = volume
        self.volume_list = ["⏹"] * self.volume_level + [" "] * (10 - self.volume_level)
        self.play_pause = "⏸"
        self.current_vinyl = "◐"
        self.current_vinyl_frame = 0
        self.line_list = ["-"] * 25

        if user_saves:
            if user_saves["shuffle"]:
                self.shuffle = True
                self.shuffle_symbol = "⤭"
            else:
                self.shuffle = False
                self.shuffle_symbol = "⇉"
        else:
            self.shuffle = False
            self.shuffle_symbol = "⇉"

        self.shuffled_song_list = []

        if user_saves:
            if user_saves["auto"] == "auto":
                self.loop_type = "auto"
                self.loop_type_symbol = "↬"
            else:
                self.loop_type = "one"
                self.loop_type_symbol = "⥁"
        else:
            self.loop_type = "auto"
            self.loop_type_symbol = "↬"

        self.previous_vol_lvl = 0
        self.mute_on_off = False
        self.playlist_added = False
        self.old_settings = None
        self.help_menu_toggle = False
        self.current_ms = None
        self.name_of_playlist = name_of_playlist
        self.current_index = current_index

    def check_key_presses(self):
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

    def loop_for_song(self, player, song_time, playlist):

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
                    if key in (' ', "k"):
                        self.play_pause = "▶"
                        self.click_sound.play()
                        player.pause()

                    elif key in ('d', "l"):
                        self.click_sound.play()
                        new_ms = min(player.get_time() + 10000, int(song_time * 1000))
                        player.set_time(new_ms)
                        self.sync_timeline(song_time, new_ms)

                    elif key in ('a', "j"):
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
                            self.save_data_to_last_play()

                    elif key == "o":
                        if self.volume_level > 0:
                            self.click_sound.play()
                            self.volume_level -= 1
                            self.update_volume_bar()
                            player.audio_set_volume(self.volume_level * 10)
                            self.save_data_to_last_play()

                    elif key == "s":
                        self.click_sound.play()
                        if self.shuffle:
                            self.shuffle = False
                            self.shuffle_symbol = "⇉"
                            self.save_data_to_last_play()
                        else:
                            self.shuffle = True
                            self.shuffle_symbol = "⤭"
                            self.save_data_to_last_play()

                    elif key == "e":
                        self.click_sound.play()
                        if self.loop_type == "one":
                            self.loop_type = "auto"
                            self.loop_type_symbol = "↬"
                            self.save_data_to_last_play()
                        else:
                            self.loop_type = "one"
                            self.loop_type_symbol = "⥁"
                            self.save_data_to_last_play()

                    elif key == "m":
                        player, song_time, self.current_index = self.next_song(player, playlist, self.current_index, self.shuffle)
                        self.save_data_to_last_play()

                    elif key == "n":
                        player, song_time, self.current_index = self.previous_song(player, playlist, self.current_index,
                                                                              self.shuffle)
                        self.save_data_to_last_play()

                    elif key == 'q':  # Quit
                        player.stop()
                        self.click_sound.play()
                        self.hard_clear_screen()
                        self.save_data_to_last_play()
                        break

                    elif key == '0':
                        if not self.mute_on_off:
                            self.click_sound.play()
                            self.previous_vol_lvl = self.volume_level
                            self.volume_level = 0
                            self.update_volume_bar()
                            player.audio_set_volume(self.volume_level * 10)
                            self.save_data_to_last_play()
                            self.mute_on_off = True
                        else:
                            self.click_sound.play()
                            self.volume_level = self.previous_vol_lvl
                            self.update_volume_bar()
                            player.audio_set_volume(self.volume_level * 10)
                            self.save_data_to_last_play()
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
                        player, song_time, playlist, self.current_index = self.select_playlist(player, playlist, song_time,
                                                                                          self.current_index)
                        self.save_data_to_last_play()
                        player.play()
                        self.play_pause = "⏸"

                    elif key == "z":
                        self.click_sound.play()
                        player, song_time, playlist, self.current_index = self.select_songs(player, playlist, song_time,
                                                                                       self.current_index)
                        self.save_data_to_last_play()
                        player.play()
                        self.play_pause = "⏸"

                    elif key == "h":
                        if self.help_menu_toggle == False:
                            self.help_menu_toggle = True
                        else:
                            self.help_menu_toggle = False

                if player.is_playing():
                    time.sleep(0.1)
                    self.current_ms = max(0, player.get_time())
                    total_sec = int(self.current_ms / 1000)
                    self.current_min = int(total_sec / 60)
                    self.current_sec = total_sec % 60
                    self.sync_timeline(song_time, self.current_ms)
                    self.seconds_for_vinyl += 0.1
                    if self.seconds_for_vinyl >= 1.0:
                        self.change_vinyl()
                        self.seconds_for_vinyl = 0
                    self.render(song_time, self.current_index, playlist)
                else:
                    time.sleep(0.1)

                if player.get_state() == vlc.State.Ended:
                    self.new_timeline = "========================="
                    self.play_pause = "▶"
                    self.render(song_time, self.current_index, playlist)
                    if self.loop_type == "one":
                        player, song_time, self.current_index = self.loop(player, playlist, self.current_index)
                        self.save_data_to_last_play()
                    else:
                        player, song_time, self.current_index = self.next_song(player, playlist, self.current_index, self.shuffle)
                        self.save_data_to_last_play()
        finally:
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
        self.hard_clear_screen()
        print("+==================================+")
        print("          IMPORT PLAYLIST           ")
        print("+==================================+")

        print("Please paste folder path where music is located: ", end="", flush=True)
        user_directory = input().strip()

        if user_directory == "`":
            print("Returning back...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return

        print("Please provide a name for the playlist: ", end="", flush=True)
        user_playlist_name = input().strip()

        if user_directory == "`":
            print("Returning back...")
            self.hard_clear_screen()
            self.enable_cbreak()
            time.sleep(0.5)
            return

        if user_directory and user_playlist_name:
            self.playlist_added = append_folder_to_songs_path(user_directory, user_playlist_name)
        else:
            print("Directory not found returning back...")

        time.sleep(1)
        self.hard_clear_screen()
        self.enable_cbreak()

    def render(self, song_time, current_song_index, playlist):
        self.hard_clear_screen()

        if self.help_menu_toggle == True:
            with open("help_keybinds.txt", "r") as help_data:
                print(help_data.read())
        else:
            total_min = int(song_time // 60)
            total_sec = int(song_time % 60)
            total_time_str = f"{total_min}:{total_sec:02d}"

            lines = [
                "+=================================================+",
                "",
                f"[ {self.current_vinyl} {self.song}]",
                f"[{self.new_timeline}] [{self.current_min}:{self.current_sec:02d}|{total_time_str}] ",
                f"[ {self.loop_type_symbol} {self.play_pause} {self.shuffle_symbol} ] [{"".join(self.volume_list)} {self.volume_level * 10}%] [{current_song_index + 1}/{len(playlist)}]",
                f"[{self.now_real_time}]",
                "",
                "+=================================================+",
                "",
                "[H] Help menu"
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
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        termios.tcsetattr(sys.stdin, termios.TCSANOW, old_settings)
        print("\033[?25h", end="", flush=True)

    def enable_cbreak(self):
        tty.setcbreak(sys.stdin.fileno())
        print("\033[?25l", end="", flush=True)
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

    def select_playlist(self, player, playlist, song_time, current_index):
        self.disable_cbreak(self.old_settings)
        self.hard_clear_screen()

        playlists_list = []

        for variable_name in dir(songs_path):
            if not variable_name.startswith("__"):
                playlists_list.append(variable_name)

        print("+==================================+")
        print("         SELECT A PLAYLIST          ")
        print("+==================================+")

        for index in range(0, len(playlists_list)):
            print(f"{index}. {playlists_list[index]}")

        print("\nPlease enter the number next to the playlist you want to play: ")
        playlist_index = input("").strip()

        if playlist_index == "`":
            print("Returning back...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        if not playlist_index.isdigit() or int(playlist_index) >= len(playlists_list):
            print("Invalid selection. Returning to player...")
            time.sleep(0.5)
            self.hard_clear_screen()
            self.enable_cbreak()
            return player, song_time, playlist, current_index

        player.stop()

        self.name_of_playlist = playlists_list[int(playlist_index)]
        new_playlist = getattr(songs_path, self.name_of_playlist)
        current_song_index = 0
        current_song = new_playlist[current_song_index]

        new_song_name = current_song.split("/")[-1]
        new_player = vlc.MediaPlayer(current_song)

        new_player.audio_set_volume(self.volume_level * 10)
        new_player.play()

        while new_player.get_length() <= 0:
            time.sleep(0.1)

        new_song_time = new_player.get_length() / 1000
        self.reset(new_song_name)

        self.hard_clear_screen()
        self.enable_cbreak()

        return new_player, new_song_time, new_playlist, 0

    def select_songs(self, player, playlist, song_time, current_index):
        self.hard_clear_screen()

        start = current_index - 5
        end = current_index + 5
        select_index = current_index
        temp_select_list = []
        for song in playlist:
            temp_select_list.append(song.split("/")[-1])

        while True:
            self.hard_clear_screen()

            if start >= len(temp_select_list) - 10:
                start = max(0, len(temp_select_list) - 10)
            elif start <= 0:
                start = 0

            if end >= len(temp_select_list):
                end = len(temp_select_list)
            elif end <= 10:
                end = min(10, len(temp_select_list))

            safe_end = min(end, len(temp_select_list))

            for line_index in range(start, safe_end):
                song_name = temp_select_list[line_index]

                if line_index == select_index:
                    print(f"\x1b[2K\r        > {song_name} <")
                else:
                    print(f"\x1b[2K\r  {song_name}  ")
            print("")
            print("[Up/N] Up | [Down/M] Down | [Enter] Play | [Q] Back")
            print(f"\x1b[{safe_end - start}A", end="", flush=True)
            print(f"")

            key = self.check_key_presses()

            if key == "s":
                pass

            if key == 'q':
                self.click_sound.play()
                break

            if key == 'm':
                self.click_sound.play()
                if select_index < len(temp_select_list) - 1:
                    select_index += 1
                    if start < len(temp_select_list) - 10 and select_index > start:
                        start += 1
                        end += 1

            if key == 'n':
                self.click_sound.play()
                if select_index > 0:
                    select_index -= 1
                    if select_index < start:
                        start -= 1
                        end -= 1

            if key and len(key) == 1 and ord(key) in (10, 13):
                player.stop()
                self.click_sound.play()

                selected_song_path = playlist[select_index]
                new_song_name = temp_select_list[select_index]

                new_player = vlc.MediaPlayer(selected_song_path)
                new_player.audio_set_volume(self.volume_level * 10)
                new_player.play()

                while new_player.get_length() <= 0:
                    time.sleep(0.1)

                new_song_time = new_player.get_length() / 1000
                self.reset(new_song_name)

                self.hard_clear_screen()
                return new_player, new_song_time, playlist, select_index

            time.sleep(0.1)

        self.hard_clear_screen()
        return player, song_time, playlist, current_index

    def next_song(self, player, playlist, current_index, shuffle):
        if shuffle:
            self.shuffled_song_list.append(current_index)
            next_index = random.randint(0, len(playlist) - 1)
        else:
            next_index = (current_index + 1) % len(playlist)

        player.stop()
        self.click_sound.play()
        next_song_path = playlist[next_index]

        path_parts = next_song_path.split('/')
        file_name_with_extension = path_parts[-1]

        next_song_name = file_name_with_extension

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

        path_parts = previous_song_path.split('/')
        file_name_with_extension = path_parts[-1]
        previous_song_name = file_name_with_extension

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
        path_parts = current_song_path.split('/')
        file_name_with_extension = path_parts[-1]

        current_song_name = file_name_with_extension

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

    def hard_clear_screen(self):
        sys.stdout.write("\033[2J\033[3J\033[H\033[0m")
        sys.stdout.flush()

    def save_data_to_last_play(self):
        data_to_save = {
            "self.volume_level": self.volume_level,
            "playlist": self.name_of_playlist,
            "index_of_song": self.current_index,
            "shuffle": self.shuffle,
            "auto": self.loop_type
        }
        with open("last_played.json", "w") as user_save:
            json.dump(data_to_save, user_save, indent=4)
