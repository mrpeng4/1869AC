import widgets
import vlc
import time
import math

songs = ["audiomass-output.mp3",
         "Joy Crookes - Feet Don't Fail Me Now (Official Video).mp3",
         "Sade - Smooth Operator - Official - 1984.mp3",
         "Катя Лель - Мой мармеладный.mp3"]

current_song = songs[3]
current_song_data = current_song.split(".")
player = vlc.MediaPlayer(current_song)
player.play()

time.sleep(0.1)
length_of_song = player.get_length()/1000
widget = widgets.UiWidgets(current_song_data[0])

song_time_min = int(length_of_song // 60)
song_seconds = int(length_of_song % 60)

if length_of_song >= 60:

    print(
        f"""[-------------------------] [0:00|{int(song_time_min)}:{str(song_seconds)}]
[ ◐ {current_song_data[0]}]""",
        end="", flush=True)
    print(f"\x1b[{1}A", end="", flush=True)

else:

    print(
        f"""\r[-------------------------] [0:00|0:{round(length_of_song)}]
[ ◐ {current_song_data[0]}]""",
        end="", flush=True)
    print(f"\x1b[{1}A", end="", flush=True)


widget.loop_for_song(player,length_of_song)