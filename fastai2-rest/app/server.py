import os
import sys
import aiohttp
import asyncio
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

import io
import json
import torch
import numpy as np
from base64 import b64encode, b64decode
from fastai2.learner import load_learner
from fastai2.vision.core import PILImage


app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])

async def setup_learner():
    learn = load_learner('model.pkl')
    return learn

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

@app.route('/analyze:predict', methods=['POST'])
async def analyze(request):

    data = await request.body()
    data_json = json.loads(data)

    if 'tta' in data_json:
        tta = data_json['tta']
    else:
        tta = False

    # read and decode images
    images_b64 = data_json['images']
    images_bytes = [b64decode(img) for img in images_b64]
    images = [PILImage.create(io.BytesIO(ib)) for ib in images_bytes]

    # create fastai dataloader and get predictions
    dl = learn.dls.test_dl(images)
    if tta:
        preds,_ = learn.tta(dl=dl)
    else:
        preds,_ = learn.get_preds(dl=dl)
    
    preds_dec = [np.argmax(p) for p in preds.tolist()]
    labels = [learn.dls.vocab[pred] for pred in preds_dec]
    probabilities = [np.max(p) for p in preds.tolist()]

    # build response json
    res_list = list(zip(labels,probabilities))
    res_dicts = [{"label": d[0], "probability": d[1]} for d in res_list]
    return JSONResponse({ 'predictions': res_dicts, 'tta': tta })
    

@app.route('/analyze', methods=['GET'])
def status(request):
    return JSONResponse(dict(status='OK'))

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), log_level="info")
