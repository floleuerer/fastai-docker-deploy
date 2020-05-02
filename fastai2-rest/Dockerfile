FROM python:3.7.3-stretch

RUN pip install fastai2 aiohttp asyncio uvicorn starlette ipykernel

WORKDIR /workdir
COPY app /workdir/

EXPOSE $PORT

RUN echo "cache bust"

ENTRYPOINT ["python3.7", "server.py", "serve"]
