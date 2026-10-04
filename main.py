import os
import sys
import importlib
if sys.platform != "win32":

    try:
        stderr_fd = sys.stderr.fileno()
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, stderr_fd)
        os.close(devnull)
    except Exception as e:
        print(e.message)
import time
import re
import vlc
import widgets
import songs_path
import dotenv
from import_system import append_folder_to_songs_path
supabaseUsernameRegex = re.compile(
    r"^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*$"
) ##Based off gotrue
####SAVE DATA
from supabase import create_client
VITE_SUPABASE_URL = "https://savqeqzsvateipglohbh.supabase.co"
VITE_SUPABASE_PUBLISHABLE_KEY = "sb_publishable_CB2Whenl1QZ4p4CxllvhPw_gngL5gXv"
supabase_url = VITE_SUPABASE_URL
supabase_key = VITE_SUPABASE_PUBLISHABLE_KEY
supabase = create_client(supabase_url, supabase_key)
with open("songs_path.py", "r") as song:
    print("Hello! Welcome to 1869AC - the terminal music player!")
    print("login, signup,or continue as a guest?")
    yor = input("(l/s/g):").strip()
    if yor.lower() == "l":
        while True:
            username = input("Username:").strip()
            password = input("Password:").strip()
            real_username = username + "@gmail.com"
            try:
                response = supabase.auth.sign_in_with_password(
                    email = real_username, 
                    password = password 
                )
                print("welcome back "+ username)
                user = response.user
            except Exception as e:
                print("oh no..." +response.error.message)
    if yor.lower() == "s":
            while True:
                username = input("Username:").strip()
                if not supabaseUsernameRegex.match(username):
                    print("Sorry. No spaces, '@' or leading/trailing periods allowed")
                else:
                    break
                while True: 
                    password = input("Password:").strip()
                    real_username = username + "@gmail.com"
                    response = supabase.auth.sign_up(
                        email = real_username, 
                        password = password 
                    )
                    if error:
                        if "Password should contain at least one character of each" in error.message:
                            print("You need: 6+ characters, 1+ lowercase, 1+ uppercase, 1+ number, and 1+ special character.");
                        else:
                            print(error.message);
                    else:
                        print("Account created! Logging you in...")
                        break
    elif yor.lower() == "g":
        print("continuing as a guest!")
    else:
        print("invalid. defaulting to no.")

    if not song.read().strip():
        print(
            "It seems like there are no songs added. Please paste a folder path down below where all your music is located:")
        user_directory = input("Folder path: ").strip()
        print("Please provide a name for the playlist:")
        while True:
            user_directory_name = input("Playlist name: ").strip()
            if " " in user_directory_name:
                user_directory_name = user_directory_name.replace(" ", "_")
                break
            elif user_directory_name == "":
                print("That's not a name! Please try again with a valid name!")
            elif not user_directory_name.isidentifier():
                print("Unfortunately, your playlist must not start with a number and can only contains letters, numbers, or _ ")
            else:
                break
        answer = append_folder_to_songs_path(user_directory, user_directory_name)
        if answer:
            print("Playlist saved! Loading your music!")
            importlib.reload(songs_path)
        else:
            print("Playlist not saved! Please rerun the script to retry")

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
