#!/bin/bash

set -e

if [ $1 == "--push" ]; then
    WILL_PUSH=1
else
    WILL_PUSH=0
fi

docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t semerhi/dockerized_dash_app:latest \
    $( (($WILL_PUSH == 1)) && printf %s '--push') .
