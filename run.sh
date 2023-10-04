#!/bin/bash

# Parámetros con valores predeterminados
[ "$1" ] && QUERIES_FILE=$1 || QUERIES_FILE=./queries.json
# [ "$2" ] && ENV_FILE=$2 || ENV_FILE=./.env
[ "$2" ] && OUTPUTS_DIR=$2 || OUTPUTS_DIR=./outputs
[ "$3" ] && IMAGE_VERSION=$3 || IMAGE_VERSION=v1


# Verificar cada parámetro y construir el comando Docker
if [ "$QUERIES_FILE" == "-" ]; then
    QUERIES_FILE=./queries.json
fi



# if [ "$ENV_FILE" == "-" ]; then
#     ENV_FILE=./.env
    
# fi

if [ "$OUTPUTS_DIR" != "-" ]; then
OUTPUTS_DIR="./outputs"
fi

DOCKER_CMD="docker run"


QUERIES_FILE=$(realpath $QUERIES_FILE)
DOCKER_CMD="$DOCKER_CMD -v $QUERIES_FILE:/src/queries.json"
# ENV_FILE=$(realpath $ENV_FILE)
# DOCKER_CMD="$DOCKER_CMD --env-file $ENV_FILE"
OUTPUTS_DIR=$(realpath $OUTPUTS_DIR)
DOCKER_CMD="$DOCKER_CMD -v $OUTPUTS_DIR:/src/outputs"
# DOCKER_CMD="$DOCKER_CMD --network mongo_default"
DOCKER_CMD="$DOCKER_CMD santosdev20/googlemapsscrapping:$IMAGE_VERSION"

echo "$DOCKER_CMD"
eval $DOCKER_CMD


# docker run -v /home/informatica/devme/google-maps-scr/scrapper/queriesExample.json:/src/queries.json --env-file /home/informatica/devme/google-maps-scr/scrapper/.env -v /home/informatica/devme/google-maps-scr/scrapper/outputs:/src/outputs --network mongo_default santosdev20/googlemapsscrapping:v1
