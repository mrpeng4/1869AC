import json
import os
import sys

stderr_fd = sys.stderr.fileno()
devnull = os.open(os.devnull, os.O_WRONLY)
os.dup2(devnull, stderr_fd)
os.close(devnull)

import time
import vlc
import widgets
import songs_path
from import_system import append_folder_to_songs_path
import re
import importlib
from pathlib import Path

def sync_playlists_with_folders():
    valid_exts = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}

    with open("songs_path.py", "r", encoding="utf-8") as f:
        content: str = f.read()

    # finds every "# Auto-imported playlist from: <folder>" + the playlist name under it
    sources = re.findall(r"# Auto-imported playlist from: (.+)\n(\w+) = \[", content)
    if not sources:
        print("Sync: no imported playlists to check.")
        return

    changed = False
    for folder, name in sources:
        folder = str(folder).strip()
        name = str(name)
        old = getattr(songs_path, name, [])
        path = Path(folder)

        if not path.is_dir():
            print(f"[{name}] source folder not found, skipped: {folder}")
            continue

        new = [str(p) for p in path.rglob('*') if p.suffix.lower() in valid_exts]
        old_set, new_set = set(old), set(new)
        added = sorted(new_set - old_set)
        removed = [s for s in old if s not in new_set]

        if not added and not removed:
            print(f"[{name}] up to date ({len(old)} songs)")
            continue

        # keep existing order, drop deleted songs, append new ones
        updated = [s for s in old if s in new_set] + added
        block = f"{name} = [\n" + "".join(f"    {repr(s)},\n" for s in updated) + "]"

        pattern = re.compile(rf"^{re.escape(name)} = \[\n.*?^\]", re.S | re.M)
        content = pattern.sub(lambda m: block, content, count=1)
        changed = True

        print(f"[{name}] updated: +{len(added)} added, -{len(removed)} removed")
        for s in added:
            print(f"   + {Path(s).name}")
        for s in removed:
            print(f"   - {Path(s).name}")

    if changed:
        with open("songs_path.py", "w", encoding="utf-8") as f:
            f.write(content)
        importlib.reload(songs_path)  # so the playlist menu sees the new data

        time.sleep(2)


sync_playlists_with_folders()

with open("songs_path.py", "r") as song:
    if not song.read().strip():
        while True:
            print("\033[H\033[2J", end="", flush=True)
            print("+=======================================================================+")

            print(
                "It seems like there are no songs added. Please paste a folder path down below where all your music is located:")
            user_directory = input("Folder path: ").strip()
            if user_directory == "`":
                continue
            print("Please provide a name for the playlist:")
            user_directory_name = input("Playlist name: ").strip()
            if user_directory == "`":
                continue

            if "" != user_directory and "" != user_directory_name:
                answer = append_folder_to_songs_path(user_directory, user_directory_name)
                if answer:
                    print("Playlist saved! Please rerun the script to load your music.")
                    print("\033[H\033[2J", end="", flush=True)
                    break
                else:
                    print("Playlist not saved! Please rerun the script to retry")

playlists_list = []

for variable_name in dir(songs_path):
    if not variable_name.startswith("__"):
        playlists_list.append(variable_name)

while True:
    print("+==================================+")
    print("         SELECT A PLAYLIST          ")
    print("+==================================+")

    for index in range(0, len(playlists_list)):
        print(f"{index}. {playlists_list[index]}")
    print("\nPress the \"z\" to play the last song you played")
    print("Please enter the number next to the playlist you want to play: ")
    playlist_index = input().strip().lower()

    if playlist_index == "z":

        with open("last_played.json", "r") as user_saves_raw:
            user_saves = json.load(user_saves_raw)

        if user_saves:

            name_for_Playlist = user_saves["playlist"]
            playlist = getattr(songs_path, name_for_Playlist)
            current_song_index = user_saves["index_of_song"]
            current_song = playlist[current_song_index]
            current_song_name = current_song.split("/")[-1]

            player = vlc.MediaPlayer(current_song)
            player.play()
            volume = user_saves["self.volume_level"]
            player.audio_set_volume(volume * 10)

            data_to_save = {
                "self.volume_level": volume,
                "playlist": name_for_Playlist,
                "index_of_song": current_song_index
            }
            with open("last_played.json", "w") as user_save:
                json.dump(data_to_save, user_save, indent=4)

            break
        else:
            pass
    else:
        if not playlist_index.isdigit() or int(playlist_index) >= len(playlists_list):
            print("Invalid selection.")
        else:
            name_for_Playlist = playlists_list[int(playlist_index)]
            playlist = getattr(songs_path, name_for_Playlist)
            current_song_index = 0
            current_song = playlist[current_song_index]
            current_song_name = current_song.split("/")[-1]

            player = vlc.MediaPlayer(current_song)
            player.play()

            with open("last_played.json", "r") as user_saves_raw:
                user_saves = json.load(user_saves_raw)

            if user_saves:
                volume = user_saves["self.volume_level"]
                player.audio_set_volume(volume * 10)
            else:
                volume = 10
                player.audio_set_volume(volume * 10)

            data_to_save = {
                "self.volume_level": volume,
                "playlist": name_for_Playlist,
                "index_of_song": current_song_index
            }
            with open("last_played.json", "w") as user_save:
                json.dump(data_to_save, user_save, indent=4)
            break


while player.get_length() <= 0:
    time.sleep(0.1)
length_of_song = player.get_length() / 1000.0
widget = widgets.UiWidgets(current_song_name, player, name_for_Playlist, current_song_index, volume)

print("\033[3J\033[H\033[2J", end="", flush=True)

widget.loop_for_song(player, length_of_song, playlist)