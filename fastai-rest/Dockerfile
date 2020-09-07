FROM python:3.8.5-slim-buster

RUN pip install fastai aiohttp asyncio uvicorn starlette ipykernel

WORKDIR /workdir
COPY app /workdir/

EXPOSE $PORT

RUN echo "cache bust"

ENTRYPOINT ["python3.8", "server.py", "serve"]
