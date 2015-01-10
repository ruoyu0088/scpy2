import shutil
from os import path

folder = path.dirname(__file__)

shutil.rmtree(path.join(folder, "README_files"))