import json
import glob
from base64 import b64encode, b64decode

files = glob.glob('images/*.sm.png')

b64list = []

for f in files:
# load images in batch and base64 encode them
    with open(f, 'rb') as open_file:
        byte_content = open_file.read()

    base64_bytes = b64encode(byte_content)
    base64_string = base64_bytes.decode('utf-8')

    b64list.append(base64_string)


data = {'images': b64list}

with open('examples.json', 'w') as outfile:
    json.dump(data, outfile)