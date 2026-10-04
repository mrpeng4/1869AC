import os
import sys
import importlib
import time
import vlc
import widgets
import songs_path
from import_system import append_folder_to_songs_path

# Clean stderr suppression for libVLC without breaking file descriptors
if sys.platform != "win32":
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 2)  # File descriptor 2 is stderr
        os.close(devnull)
    except Exception:
        pass


def clear_screen():
    """Cross-platform terminal clear."""
    os.system("cls" if os.name == "nt" else "clear")

with open("songs_path.py", "r") as song:
    print("+====================================================+")
    print("Hello! Welcome to 1869AC - the terminal music player!")
    print("Continue as a guest or login to save your playlists to the cloud!")
    print("( a/ g ): ")
    yor = input("").strip()
    if not song.read().strip():
        print(
            "It seems like there are no songs added. Please paste a folder path down below where all your music is located:"
        )
        print("Folder path: ")
        user_directory = input("").strip()
        print("Please provide a name for the playlist:")
        while True:
            print("Playlist name: ")
            user_directory_name = input("").strip()
            if " " in user_directory_name:
                user_directory_name = user_directory_name.replace(" ", "_")
                break
            elif user_directory_name == "":
                print("That's not a name! Please try again with a valid name!")
            elif not user_directory_name.isidentifier():
                print(
                    "Unfortunately, your playlist must not start with a number and can only contains letters, numbers, or _ "
                )
            else:
                break
        answer = append_folder_to_songs_path(user_directory, user_directory_name)
        if answer:
            print("Playlist saved! Loading your music!")
            importlib.reload(songs_path)
        else:
            print("Playlist not saved! Please rerun the script to retry")

playlists_list = [v for v in dir(songs_path) if not v.startswith("__")]

print("+==================================+")
print("         SELECT A PLAYLIST          ")
print("+==================================+")

for index, name in enumerate(playlists_list):
    print(f"{index}. {name}")

print("\nPlease enter the number next to the playlist you want to play: ")
playlist_index = input("").strip()

if not playlist_index.isdigit() or int(playlist_index) >= len(playlists_list):
    print("Invalid selection. Please rerun and pick a valid playlist number.")
    sys.exit()

name_for_Playlist = playlists_list[int(playlist_index)]
playlist = getattr(songs_path, name_for_Playlist)
current_song_index = 0
current_song = playlist[current_song_index]

current_song_name = os.path.basename(current_song)
player = vlc.MediaPlayer(current_song)
player.play()

while player.get_length() <= 0:
    time.sleep(0.1)

length_of_song = player.get_length() / 1000.0
widget = widgets.UiWidgets(current_song_name, player)

clear_screen()
widget.loop_for_song(player, length_of_song, playlist, current_song_index)