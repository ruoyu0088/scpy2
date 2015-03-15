import os
from os import path
import re
import warnings


def search_program_files(pattern, check_path):
    key_names = ["ProgramFiles", "ProgramW6432"]
    for key in key_names:
        if key in os.environ:
            program_files = os.environ[key]
            for folder_name in os.listdir(program_files):
                if re.match(pattern, folder_name, re.IGNORECASE):
                    full_path = path.join(program_files, folder_name, check_path)
                    if path.exists(full_path):
                        return full_path


GraphvizPath = search_program_files("graphviz.*", r"bin\dot.exe")
if GraphvizPath is None:
    warnings.warn("Graphviz not found")

InkscapePath = search_program_files("inkscape.*", "inkscape.exe")
if InkscapePath is None:
    warnings.warn("Inkscape not found")