import os
import sys

if sys.platform != "win32":
    try:
        stderr_fd = sys.stderr.fileno()
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, stderr_fd)
        os.close(devnull)
    except Exception as e:
        print(e.message)

import time
import vlc
import widgets
import songs_path
from import_system import append_folder_to_songs_path

with open("songs_path.py", "r") as song:
    if not song.read().strip():
        print(
            "It seems like there are no songs added. Please paste a folder path down below where all your music is located:")
        user_directory = input("Folder path: ").strip()
        print("Please provide a name for the playlist:")
        user_directory_name = input("Playlist name: ").strip()

        answer = append_folder_to_songs_path(user_directory, user_directory_name)
        if answer:
            print("Playlist saved! Please rerun the script to load your music.")
        else:
            print("Playlist not saved! Please rerun the script to retry")
        sys.exit()

playlists_list = []

for variable_name in dir(songs_path):
    if not variable_name.startswith("__"):
        playlists_list.append(variable_name)

print(" ")
print("         SELECT A PLAYLIST          ")
print(" ")

for index in range(0, len(playlists_list)):
    print(f"{index}. {playlists_list[index]}")

playlist_index = input("\nPlease enter the number next to the playlist you want to play: ").strip()

if not playlist_index.isdigit() or int(playlist_index) >= len(playlists_list):
    print("Invalid selection. Please rerun and pick a valid playlist number.")
    exit()

name_for_Playlist = playlists_list[int(playlist_index)]
playlist = getattr(songs_path, name_for_Playlist)
current_song_index = 0
current_song = playlist[current_song_index]

current_song_name = current_song.split("/")[-1]
player = vlc.MediaPlayer(current_song)
player.play()

while player.get_length() <= 0:
    time.sleep(0.1)

length_of_song = player.get_length() / 1000.0
widget = widgets.UiWidgets(current_song_name, player)

print("\033[3J\033[H\033[2J", end="", flush=True)

widget.loop_for_song(player, length_of_song, playlist, current_song_index)
