from pathlib import Path
import songs_path

def append_folder_to_songs_path(folder_path, playlist_name):

    playlists_list = []

    for variable_name in dir(songs_path):
        if not variable_name.startswith("__"):
            playlists_list.append(variable_name)

    if playlist_name in playlists_list:
        print("this name is already taken please and try something other")

        return False

    else:
        path = Path(folder_path).expanduser().resolve()
        if not path.is_dir():
            print(f"Error: Directory '{folder_path}' not found.")
            return False

        valid_exts = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
        audio_files = [str(f) for f in path.rglob('*') if f.suffix.lower() in valid_exts]
        if not audio_files:
            print(f"No audio files found in '{folder_path}'.")
            return False

        python_code = f"\n# Auto-imported playlist from: {path}\n{playlist_name} = [\n"
        python_code += "".join(f"    {repr(audio)},\n" for audio in audio_files)
        python_code += "]\n"
        with open("songs_path.py", "a", encoding="utf-8") as f:
            f.write(python_code)
        print(f"Added {len(audio_files)} songs to songs_path.py as list '{playlist_name}'.")
        return True