import sys
import time

RESET = "\033[0m"

THEMES = [
    {
        "id": 0,
        "name": "Cyberpunk Neon",
        "border": "\033[38;5;51m",
        "title": "\033[38;5;201m",
        "accent": "\033[38;5;226m",
        "dim": "\033[38;5;242m",
        "reset": RESET
    },
    {
        "id": 1,
        "name": "Retro Amber",
        "border": "\033[38;5;130m",
        "title": "\033[38;5;214m",
        "accent": "\033[38;5;220m",
        "dim": "\033[38;5;238m",
        "reset": RESET
    },
    {
        "id": 2,
        "name": "Monochrome Minimal",
        "border": "\033[38;5;240m",
        "title": "\033[38;5;255m",
        "accent": "\033[38;5;250m",
        "dim": "\033[38;5;236m",
        "reset": RESET
    },
    {
        "id": 3,
        "name": "Soft Pastel",
        "border": "\033[38;5;189m",
        "title": "\033[38;5;217m",
        "accent": "\033[38;5;157m",
        "dim": "\033[38;5;245m",
        "reset": RESET
    }
]

SPEED_PRESETS = [0.75, 1.0, 1.25, 1.5, 2.0]
current_speed_idx = 1
active_theme_idx = 0

custom_colors = {
    "border": None,
    "title": None,
    "accent": None,
    "dim": None
}


def get_current_speed():
    if 0 <= current_speed_idx < len(SPEED_PRESETS):
        return SPEED_PRESETS[current_speed_idx]
    return 1.0


def change_speed(direction="up"):
    global current_speed_idx

    min_index = 0
    max_index = len(SPEED_PRESETS) - 1

    if direction == "up":
        if current_speed_idx < max_index:
            current_speed_idx += 1
        else:
            current_speed_idx = max_index

    elif direction == "down":
        if current_speed_idx > min_index:
            current_speed_idx -= 1
        else:
            current_speed_idx = min_index

    return SPEED_PRESETS[current_speed_idx]


def reset_speed():
    global current_speed_idx
    current_speed_idx = 1
    return SPEED_PRESETS[current_speed_idx]


def cycle_next_theme():
    global active_theme_idx
    total_themes = len(THEMES)
    active_theme_idx = (active_theme_idx + 1) % total_themes
    return THEMES[active_theme_idx]["name"]


def set_theme_by_id(target_id):
    global active_theme_idx
    if 0 <= target_id < len(THEMES):
        active_theme_idx = target_id
        return True
    return False


def get_current_palette():
    global active_theme_idx
    global custom_colors

    total_themes = len(THEMES)
    safe_index = active_theme_idx % total_themes
    base = THEMES[safe_index]

    if custom_colors["border"] is not None:
        resolved_border = custom_colors["border"]
    else:
        resolved_border = base["border"]

    if custom_colors["title"] is not None:
        resolved_title = custom_colors["title"]
    else:
        resolved_title = base["title"]

    if custom_colors["accent"] is not None:
        resolved_accent = custom_colors["accent"]
    else:
        resolved_accent = base["accent"]

    if custom_colors["dim"] is not None:
        resolved_dim = custom_colors["dim"]
    else:
        resolved_dim = base["dim"]

    palette = {
        "name": base["name"],
        "border": resolved_border,
        "title": resolved_title,
        "accent": resolved_accent,
        "dim": resolved_dim,
        "reset": base["reset"]
    }
    return palette


def set_custom_color(target_element, color_code_256):
    global custom_colors

    valid_elements = ["border", "title", "accent", "dim"]
    if target_element not in valid_elements:
        return False

    try:
        code_int = int(color_code_256)
        if 0 <= code_int <= 255:
            custom_colors[target_element] = f"\033[38;5;{code_int}m"
            return True
        return False
    except ValueError:
        return False


def reset_custom_colors():
    global custom_colors
    custom_colors["border"] = None
    custom_colors["title"] = None
    custom_colors["accent"] = None
    custom_colors["dim"] = None


def clear_terminal():
    print("\033[H\033[2J", end="", flush=True)


def get_shortcuts_list():
    current_speed = get_current_speed()
    shortcuts = [
        ("[Space] / [K]", "Play / Pause Playback"),
        ("[D] / [->]",    "Fast Forward 10s"),
        ("[A] / [<-]",    "Rewind 10s"),
        ("[P] / [O]",     "Volume Up / Down"),
        ("[0]",           "Toggle Mute / Unmute"),
        ("[[] / []]",     f"Speed Down / Up (Current: {current_speed}x)"),
        ("[S]",           "Toggle Shuffle Mode"),
        ("[E]",           "Toggle Repeat Mode"),
        ("[M] / [N]",     "Next / Previous Track"),
        ("[T]",           "Cycle Theme Presets"),
        ("[U]",           "Custom Text Color Picker"),
        ("[H] / [?]",     "Toggle This Help Screen"),
        ("[Q]",           "Exit Deck")
    ]
    return shortcuts


def build_shortcut_row(key_cmd, desc, box_width, acc, r, b):
    key_formatted = f"{acc}{key_cmd:<18}{r}"
    desc_formatted = f": {desc}"

    visible_length = 18 + 2 + len(desc)
    pad_size = box_width - visible_length

    if pad_size < 0:
        pad_size = 0

    spaces = " " * pad_size
    row = f"{b}|{r}  {key_formatted}{desc_formatted}{spaces}{b}|{r}"
    return row


def show_help_box():
    palette = get_current_palette()
    b = palette["border"]
    t = palette["title"]
    acc = palette["accent"]
    dim = palette["dim"]
    r = palette["reset"]

    box_width = 64
    header_text = "KEYBOARD SHORTCUTS & HELP"
    footer_text = "Press [Enter] to return..."

    clear_terminal()

    top_border = f"{b}+" + "-" * box_width + f"+{r}"
    print(top_border)

    title_display = f"{t}{header_text}{r}"
    title_centered = title_display.center(box_width + len(t) + len(r))
    print(f"{b}|{r}" + title_centered + f"{b}|{r}")

    divider = f"{b}+" + "-" * box_width + f"+{r}"
    print(divider)

    shortcuts = get_shortcuts_list()
    for key_cmd, desc in shortcuts:
        row = build_shortcut_row(key_cmd, desc, box_width, acc, r, b)
        print(row)

    print(divider)

    footer_display = f"{dim}{footer_text}{r}"
    footer_centered = footer_display.center(box_width + len(dim) + len(r))
    print(f"{b}|{r}" + footer_centered + f"{b}|{r}")

    print(top_border)
    sys.stdout.flush()

    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass

    clear_terminal()
    print(RESET, end="", flush=True)


def prompt_custom_color_picker():
    clear_terminal()
    print("--- CUSTOM TEXT COLOR PICKER ---")
    print("Choose element: border / title / accent / dim")
    element = input("Element: ").strip().lower()

    if element in ["border", "title", "accent", "dim"]:
        print("Enter ANSI 256 code (0 to 255):")
        code = input("Color Code: ").strip()
        success = set_custom_color(element, code)
        if success:
            print("Color updated successfully!")
        else:
            print("Invalid color code.")
    else:
        print("Invalid element name.")

    time.sleep(1.2)
    clear_terminal()