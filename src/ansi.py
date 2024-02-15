# Usage: string = f"{ansi.normal.fg.red}wow awesome{ansi_reset}"
# available colors (ansi_colors, ansi_bg_colors) and styles (ansi_formatt) are listed below

from dotted_dict import DottedDict as dotted_dict
import re

ansi_colors = {"gray": 30, "red": 31, "green": 32, "yellow": 33, "blue": 34, "pink": 35, "cyan": 36, "white": 37}
ansi_bg_colors = {"dark_blue": 40, "orange": 41, "marble_blue": 42, "turqouise": 43, "gray": 44, "indigo": 45, "light_gray": 46, "white": 47}
ansi_formatt = {"normal": 0, "bold": 1, "underline": 4}

ansi = dotted_dict()
ansi_reset = "\u001b[0m"

for formatt in ["normal", "bold", "underline"]:
    ansi[formatt] = dotted_dict()
    for typee in ["bg", "fg"]:
        ansi[formatt][typee] = dotted_dict()
        if typee == "bg":
            for key, color in ansi_bg_colors.items():
                ansi[formatt][typee][key] = f"\u001b[{ansi_formatt[formatt]};{color}m"
        elif typee == "fg":
            for key, color in ansi_colors.items():
                ansi[formatt][typee][key] = f"\u001b[{ansi_formatt[formatt]};{color}m"

ansi_split_keys = [" "] # space included for nicer word wrapping
for formatt_key, formatt_data in ansi.items():
    for type_key, type_data in formatt_data.items():
        for color_key, color_data in type_data.items():
            ansi_split_keys.append(re.escape(color_data))

def ansi_split_str_from_words(l, s):
    m = re.split(rf"({'|'.join(l)})", s)
    return [i for i in m if i]

def ansi_wrap(text):
    segments = ansi_split_str_from_words(ansi_split_keys, text)
    
    output = []
    current = "```ansi\n"
    last_ansi_code = None
    for segment in segments:
        if "\u001b" in segment and segment != ansi_reset:
            last_ansi_code = segment
        if len(current) + len(segment) < 1980:
            current += segment
        else:
            current += "```"
            output.append(current)
            current = "```ansi\n"
            if last_ansi_code:
                current += last_ansi_code
                last_ansi_code = None

    if current != "```ansi\n":
        current += "```"
        output.append(current)

    return output