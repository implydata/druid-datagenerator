#!/bin/bash
export DOCKER_BUILDKIT=1
docker buildx create --use --name=qemu
dcoker buildx inspect --bootstrap
docker buildx build --platform linux/amd64,linux/arm64 --tag imply/datagen:latest --push .
