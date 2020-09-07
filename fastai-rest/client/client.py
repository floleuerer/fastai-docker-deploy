from base64 import b64encode, b64decode
import json
import math
import requests
import os
import glob
import shutil

url = 'http://localhost:8080/analyze:predict'

files = glob.glob("/path/to/images/*.jpg")

bs = 10
batches = int(math.ceil(len(files) / bs))
print('batches', str(batches))

for i in range(batches):
    print("batch: ", str(i))
    img_from = int(i*bs)
    img_to = int((i+1)*bs)
    batch_files = files[img_from:img_to]
    images = []
    for f in batch_files:

        # load images in batch and base64 encode them
        with open(f, 'rb') as open_file:
            byte_content = open_file.read()

        base64_bytes = b64encode(byte_content)
        base64_string = base64_bytes.decode('utf-8')

        images.append(base64_string)
        
    # build request JSON
    raw_data = {
        "images": images,
        "tta": False
        }

    # make request
    r = requests.post(url, json=raw_data)
    if r.status_code == 200:
        r_json = r.json()
        # print predictions
        for i,p in enumerate(r_json['predictions']):
            print(r_json['predictions'][i]['label'], r_json['predictions'][i]['probability'])

    else:
        print(f'error: return code != 200 -> got return code {r.status_code}')
        print(r_json)
       



