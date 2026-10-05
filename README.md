# 1869AC

**1869AC** is an animated, terminal-based music player built in Python. Powered by `libvlc` and `pygame.mixer`, it features multi-playlist support, multiple folder importing, volume controls, shuffle queueing, and a custom ANSI terminal interface with UI sound effects.

**_Just made a new website for our app rn it is just a simple website for our app later it is gonna become a user dashboard for the online mode/version of our app._**
_In the future it will also be online! At this website: https://www.thepillu.site/. Then it will be available both online and offline!_

These are also work in progress features!: Preset Themes, Help Box, Speed Control, aur Custom Colors these are not working 

## Features
- **Animation:** Dynamic 12-Slot ASCII Animated Audio Wave Bars

- **Symbols:** Circular Quarter Symbols For Spinning Vinyl Animation

- **Volume:** Filled Block Indicator For Volume Level Display

- **Layout:** Clean Bordered Box Layout With Dynamic Row Formatting

- **Music Importer:** Scans any directory on your computer for audio files (`.mp3`, `.wav`, `.flac`, `.m4a`, `.ogg`) and saves them as custom named playlists.
  
- **Startup Menu:** Displays available playlists on launch for quick selection.
  
- **Track Navigation:** Next (`m`) and previous (`n`) song controls with history shuffle memory.
  
- **Volume & Sound Effects:** Real-time 10-level volume adjustments (`o`/`p`) complete with audio feedback using `pygame.mixer`.
  
- **Playback Modes:** Shuffle mode (`s`) and single-track with live visual status symbols.
  
- **Terminal UI Dashboard:** Renders a progress timeline bar, current date/clock, elapsed vs. total time, and an animated vinyl indicator.
  
- **Clean Console Output:** Automatically suppresses low-level VLC stderr logging to preserve terminal clean-ups.

- **Loop functionality:** loop key (`e`) can switch between single song loop and continue playlist.
  
- **Playlist importer:** by putting the path of the directory where all your songs are stored it automatically reads and save it to a .py file and then reads it for you and plays the music live from the folder and saves it as a playlist witch you can switch between.

- **Playlist selector:** select and choose between your favorite playlists.

- **Song selector:** select and choose between your favorite Songs.

- **Guest and Account Access:** store your playlists with a supabase backend! (may be a bit buggy at the moment but it should work!)

---

## Key Controls

| Key | Action |
| :--- | :--- |
| **`Space`** or **`k`** | Play / Pause|
| **`m`** | Next Track|
| **`n`** | Previous Track|
| **`d`** or **`l`** | Seek Forward (10 seconds)|
| **`a`** or **`j`** | Seek Backward (10 seconds)|
| **`p`** | Volume Up 10%|
| **`o`** | Volume Down 10%|
| **`s`** | Toggle Shuffle Mode|
| **`e`** | Toggle Repeat Mode (Auto / Single Loop) (doesn't work for now, just the symbol changes)|
| **`q`** | Quit Player
| **`c`** | Import new music folder as playlist
| **`x`** | Open Playlist Switcher menu
| **`z`** | Open Song Switcher menu

---

## Requirements & Installation

### Prerequisites
1. **Python 3.8+**
2. **It requires `vlc` to run because the backend is just vlc media player 😅!!**
3. **System VLC Media Player** (Required by `python-vlc` bindings):
   - **macOS:** `brew install --cask vlc`
   - **Linux (Ubuntu):** `sudo apt install vlc`

### Install

```
brew install --cask vlc
brew tap mrpeng4/tap
brew install ac1869
1869ac
```

### Notes
- Works on windows, mac and linux
- Requires Homebrew(mac only) and VLC
- Your playlists are stored in `~/Library/Application Support/1869AC/` and are never overwritten by updates
- You can also store in the cloud with a supabase backend

### Update (if already using a previous version)
```
brew update
brew upgrade ac1869
```
