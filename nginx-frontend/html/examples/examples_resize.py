import os, sys
from PIL import Image
import glob

size = 300, 300

files = glob.glob('images/*')

for infile in files:
    outfile = os.path.splitext(infile)[0] + ".sm.png"
    if infile != outfile:
        try:
            im = Image.open(infile)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(outfile, "PNG")
        except IOError:
            print("cannot create thumbnail for '%s'" % infile)