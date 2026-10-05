import os
import sys
import importlib
import time
import vlc
import widgets
import songs_path
from import_system import append_folder_to_songs_path
from auth import account
playlists_list = []
##SUPABASE STUFF
name2 = "guest"
username = "guest"
jsdoit = False
from supabaseclient import supabase
##
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
    ### handle auth
    print("+====================================================+")
    print("Hello! Welcome to 1869AC - the terminal music player!")
    print("Continue as a guest or login to save your playlists to the cloud!")
    print("( l/ g ): ")
    choice = input("").strip()
    if choice.lower() == 'l':
        name2 = account()
        if name2 != "guest":
            #user exists need to sync to cloud
            try:
                response = supabase.table("users").select("songs").eq("id", name2).maybe_single().execute()
                if response is None or response.data is None:
                    jsdoit = True
                else:
                    ##SONG JSON THERE
                    playlists_list = response.data["songs"] or []
            except Exception as e:
                print(response.error.message)
    elif choice.lower() == 'g':  
        print("continuing as a guest...") 
    else:
        print("invalid. defaulting to guest mode.") 
    print("+====================================================+")
    ###
    if not song.read().strip() or jsdoit is True:
        
        print(
            "It seems like there are no songs added. Please paste a folder path down below where all your music is located:"
        )
        print("Folder path: ")
        user_directory = input("").strip()
        user_directory_name = ""
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
            ##CHECK IF LOGGED IN 
            if name2 != "guest":
                print("TRYING")
                oldSongs = []
                try:
                    response = supabase.table("users").select("songs").eq("id", name2).maybe_single().execute()
                    if response is None or response.data is None:
                        oldSongs = []
                    else:
                        oldSongs = response.data["songs"]
                    response = supabase.table("users").upsert({
                        "id": name2,
                        "songs": oldSongs + [user_directory_name]
                    }).execute()
                except Exception as e: 
                    print(response.error.message)
        else:
            print("Playlist not saved! Please rerun the script to retry")
if name2 == "guest":
    playlists_list = [v for v in dir(songs_path) if not v.startswith("__")]
else:
    response = supabase.table("users").select("songs").eq("id", name2).maybe_single().execute()
    if response is not None: 
        playlists_list = response.data["songs"]
        print(playlists_list)
    else:
        print("Something went wrong. try again")
        sys.exit()

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
if name2 != "guest":
    try:
        print("name"+name)
        response = supabase.auth.get_user()
        username_with_email = response.user.email
        username = username_with_email.split("@")[0]
    except Exception as e: 
        print(response.error.message)
length_of_song = player.get_length() / 1000.0
widget = widgets.UiWidgets(current_song_name, player, username)

clear_screen()
widget.loop_for_song(player, length_of_song, playlist, current_song_index, username)

