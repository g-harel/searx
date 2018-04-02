#!/bin/sh

IMAGE_NAME=sx

docker build -t $IMAGE_NAME .
docker run $IMAGE_NAME
docker rmi -f $IMAGE_NAME
