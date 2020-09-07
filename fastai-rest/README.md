# Deploy fastai models with Docker

A Docker image for deploying [fastai](https://www.fast.ai/) models. Currently supports image classification models but i will add more use-cases later. The code is based on [fastai-serving](https://github.com/developmentseed/fastai-serving).

See my [Blog Post](https://floleuerer.github.io/2020/04/26/deploy-digitalocean.html) on how to deploy your fastai model for 5 $ per month on [Digital Ocean](http://www.digitalocean.com). The `fastai-rest` image can also easily be deployed on [Google Cloud Run](https://cloud.google.com/run) - see the instructions below.

Supports `text` and `images` as input types and `classification` and `multi labeling` as ouput types / tasks.

## Prerequisites

To build and test the image locally you need to install [Docker](https://docs.docker.com/get-docker/).

## Build & Run

First train and export a fastai `Learner` with [`learn.export()`](https://docs.fast.ai/basic_train.html#Deploying-your-model). Put the model file to `app/model.pkl`.

Then build and run the docker image with the following commands.

### Docker

```
$ PORT=8080 && docker build -f Dockerfile -t org/image:tag .
```

Run the Docker-Image:

```
$ docker run --rm -p 8080:8080 -t org/image:tag .
```

### Google Cloud Run

```
gcloud builds submit --tag gcr.io/<project-name>/<image-name>
```

Deploy and run on Cloud Run

```
gcloud run deploy --image gcr.io/<project-name>/<image-name> --platform managed --memory 1024M
```


## Use

The API currently has two endpoints:

### `POST /analyze:predict`

The `input_type` (image or text) is inferred from the Learner type (TextLearner -> text input. all other learners -> image input). You can set the `input_type` explicitly in your JSON request.

```js
{
  'input_type'='image' # for image input
  'input_type'='text' # for text input
}
```

#### Vision / Images Input

Accepts a JSON request in the form:

```js
{
  "images": ['base64 encoded image',
              'another base64 encoded image',
              '...'],
  "tta": False
}
```
Where `images` is a list of base64 encoded images and `tta` a bool variable to enable / disable [`test time augmentation`](https://docs.fast.ai/basic_train.html#Test-time-augmentation).

#### Text Input

Accepts a JSON request in the form:

```js
{
  "texts": ['text 1 ...',
              'text 2 ...',
              '...']
}
```

### Output

#### Classification / Multi Labeling Output

The `output_type` is inferred by the loss_func of your lerner.
- `CrossEntropy*` loss function -> classification - `output_type = 'class'`
- `BCEWithLogits*` loss function -> multi labeling - `output_type = 'label'`

To set the `ouput_type` explicitly add `ouput_type` to your JSON request.

Returns a JSON response in the form:

```js
{
  "predictions": [
    { 
      "label": "predicted label(s)",
      "probability": 0.873
    },
        { 
      "label": "predicted label(s) 2",
      "probability": 0.2123
    }
  ]
}

```

### `GET /analyze`

Returns an HTTP Status of `200` as long as the API is running (health check).

## client.py

See `client/client.py` for an example how to make API calls.