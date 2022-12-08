# Dash App Demo - German Credit Model

This is a Dockerized version of the [German Credit Dash WebApp](https://github.com/GaussTheBoss/dash_webapp_german_credit).

![Dash Webapp](webapp.PNG?raw=true "Dash Webapp")

The docker image can be found [here](https://hub.docker.com/repository/docker/semerhi/dockerized_dash_app).

## Running Locally

You may either want to rebuilt the docker image, or alternatively, pull the existing image with

```
sudo docker pull semerhi/dockerized_dash_app:latest
```

then run it with 

```
sudo docker run -p 8080:80 semerhi/dockerized_dash_app:latest
```

When you visit `http://localhost:8080/` (or `0.0.0.0:8080` depending on your operating system), you should see your app running within your Docker container.