from os import path
from glob import glob

folder = path.dirname(__file__)

for mdfn in glob(path.join(folder, "*.md")):
    with open(mdfn, "rb") as f:
        md = f.read()
        md = md.replace("/files/images/", "images/")
    with open(mdfn, "wb") as f:
        f.write(md)