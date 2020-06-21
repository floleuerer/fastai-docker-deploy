import os
import sys
import traceback
import time
import aiohttp
import asyncio
import uvicorn
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

import json
from fastai2_inference import Inferencer

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])

async def setup_learner():
    inf = Inferencer('model.pkl', input_type=None)
    return inf

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
inf = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


@app.route('/analyze:predict', methods=['POST'])
async def analyze(request):

    data = await request.body()
    data_json = json.loads(data)

    if 'tta' in data_json:
        tta = data_json['tta']
    else:
        tta = False
            

    try: 
        start_time = time.time()

        preds = inf.get_preds(data_json)
        preds_dec, labels, probabilities = inf.get_results(preds)

        inference_time = time.time() - start_time

        # build response json
        res_list = list(zip(labels,probabilities))
        res_dicts = [{"label": d[0], "probability": d[1]} for d in res_list]
        res = { 'predictions': res_dicts, 'tta': tta, "time": inference_time }
        status = 200
    except Exception as e:
        error = str(e)
        print('error: ' + error)
        print(traceback.print_exc())
        res = { "error": error }
        status = 400

    return JSONResponse(res, status_code=status)
    

@app.route('/analyze', methods=['GET'])
def status(request):
    return JSONResponse(dict(status='OK'))

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), log_level="info")
