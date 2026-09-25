import  widgets
import vlc
import time

songs = ["songs/audiomass-output.mp3",
         "songs/Joy Crookes - Feet Don't Fail Me Now (Official Video).mp3",
         "songs/Sade - Smooth Operator - Official - 1984.mp3",
         "songs/Катя Лель - Мой мармеладный.mp3"]

current_song = songs[0]
current_song_data = current_song.split(".")
current_song_name = current_song_data[0].split("/")
player = vlc.MediaPlayer(current_song)
player.play()

while player.get_length() <= 0:
    time.sleep(0.1)
length_of_song = player.get_length()/1000
widget = widgets.UiWidgets(current_song_name[1])

song_time_min = int(length_of_song // 60)
song_seconds = int(length_of_song % 60)

if length_of_song >= 60:

    print(
        f"""[-------------------------] [0:00|{int(song_time_min)}:{str(song_seconds)}] [ ⏮  ▶ ⏭ ]
[ ◐ {current_song_name[1]}]""",
        end="", flush=True)
    print(f"\x1b[{1}A", end="", flush=True)

else:

    print(
        f"""\r[-------------------------] [0:00|0:{round(length_of_song)}] [ ⏮  ▶ ⏭ ]
[ ◐ {current_song_name[1]}]""",
        end="", flush=True)
    print(f"\x1b[{1}A", end="", flush=True)


widget.loop_for_song(player,length_of_song)
