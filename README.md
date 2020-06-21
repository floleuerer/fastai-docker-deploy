# fastai2-docker-deploy

Building DeepLearning models is really easy with [fast.ai](https://www.fast.ai) - deploying models unfortunatley is not! So i tried to find a **cheap and easy** way, to deploy models with Docker as a REST-API (folder `fastai2-rest`). Besides that, i also to develop a "frontend" component using [nginx](https://www.nginx.com) to secure the API calls by enabling SSL with **letsencrypt**. I added a small Website so you can interact with the model :). 

All of this is running on a **5 $ DigitalOcean Droplet**. See my website [Dog or HotDog?](https://dog-or-hotdog.meansqua.red/).

**If you are just intrested in deploying a model as a REST-API** see `fastai2-rest` and the README there and my [blogpost](https://floleuerer.github.io/2020/04/26/deploy-digitalocean.html). 

## Architecutre

Here's an overview of the architecture.

```
                DigitalOcean Droplet
     +-------------------------------------+
     |               Docker                |
     |                                     |
     |                      /api calls     |
     |    +-----------+  interal redirect  |
     |    |           |     http 8080      |
     |    |  fastai2  | <------------+     |
     |    |           |              |     |
     |    |           |              |     |
     |    +-----------+              |     |   dog-or-hotdog.meansqua.red/api   +------------+
     |      Container      +-----------+   |          http(s) 80/443            |            |
     |                     |           |   |       redirect to fastai2          |            |
     |                     |           | <--------------------------------------+            |
     |                     |   nginx   |   |                                    |   client   |
     |                     |           | <--------------------------------------+            |
     |                     |           |   |    dog-or-hotdog.meansqua.red      |            |
     |                     +-----------+   |         http(s) 80/443             |            |
     |                       Container     |       Website nginx/html           +------------+
     |                                     |
     +-------------------------------------+
```

## Prerequisites

### Create Droplet + Domain
- Create Docker Droplet on [DigitalOcean](https://www.digitaloceam.com) (see my [blogpost](https://floleuerer.github.io/2020/04/26/deploy-digitalocean.html) - make sure to follow the instructions and create a **swap-file**!)
- Create (sub-)domain (e.g. `dog-or-hotdog.meansqua.red`) and assign **Droplet IP**

## Setup 

The `nginx-frontend/config` and `nginx-frontend/html` folders are mounted into the Docker container. So it's **curcial to use the same the paths (so make sure to clone the repo in `/docker`)!** 

### Hostname
The hostname `dog-or-hotdog.meansqua.red` has to be replaced with your **hostname** in the following files:
```
nginx-frontend/config/default.config
nginx-html/classify.js
```

### Letsencrypt

Install certbot and create **letsencrypt** certificates
```bash
# add repositories
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update

# install certbot
sudo apt-get install certbot

# open firewall port 80 temporarily
sudo ufw allow 80/tcp

# create letscrypt certificate
sudo certbot certonly --standalone

# close firewall again
sudo ufw delete allow 80/tcp
```
The certificates are stored in `/etc/letsencrypt/live/<domainname>`.

### Clone repository

Clone this `repository` on your Droplet
```bash
mkdir /docker && cd /docker
git clone https://github.com/floleuerer/fastai2-docker-deploy.git
```

### Download fastai2-model

The fastai2 model is not part of the repository. The **Dog or HotDog** model can be downloaded [here](https://www.meansqua.red/files/model.pkl) and has to be copied to `fastai2-rest/app/model.pkl`.
```
cd /docker/fastai2-docker-deploy/fastai2-rest/app/
wget https://www.meansqua.red/files/model.pkl
```

### Build docker images

```bash
cd /docker/fastai2-docker-deploy
docker-compose build
```

## Run the App

After successfully building the docker images you can start / stop the app:
```bash
cd /docker/fastai2-docker-deploy
# start
docker-compose up -d

# stop
docker-compose down
```


## Adopt project 

To use this App with your own fastai2 image classification model, you have to make some adjustments.

### Hostname
The hostname "dog-or-hotdog.meansqua.red" has to be replaced with your hostname in the following files:

`nginx-frontend/config/default.config`
```
server {
    listen       80;
    server_name dog-or-hotdog.meansqua.red;


server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name dog-or-hotdog.meansqua.red;

    ssl_certificate /etc/letsencrypt/live/dog-or-hotdog.meansqua.red/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dog-or-hotdog.meansqua.red/privkey.pem;
```

`nginx-html/classify.js`
```
let url = "https://dog-or-hotdog.meansqua.red/api/analyze:predict";
```

### fastai2-Model

Copy your exported model (`learn.export()`) to `fastai2-rest/app/model.pkl`.

The model labels are replaced with a human friendlier text (dog -> Dog and hot_dog -> Hot Dog). Please replace and add all your class labels in `nginx-frontend/classes.json`.

```json
{
    "dog": "Dog", 
    "hot_dog": "Hot Dog"
}
```

### Add example images for random image classification
Use the python scripts in `nginx-frontend/html/examples/` to create an `examples.json` that is used for the random image classificaiton (click on drop area). 
Move `examples.json` to `ngnix-frontend/html/examples.json`.

### Rebuild the docker containers

See "Build docker images" above. 


