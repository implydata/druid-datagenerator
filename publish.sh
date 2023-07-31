#!/bin/bash
docker image build -t imply/datagen:latest .
docker push imply/datagen:latest
