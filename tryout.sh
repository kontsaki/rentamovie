#!/usr/bin/bash
if [[ "$1" = "build" ]]; then
    docker build . -t rentamovie;
elif [[ "$1" = "shell" ]]; then
    docker run\
    -it \
    --rm \
    --name rentamovie \
    -v `pwd`:/opt/rentamovie/ \
    -w /opt/rentamovie/ \
    --network bridge \
    -e APP_DATABASE=':memory:' \
    rentamovie \
    bash
elif [[ "$1" = "test" ]]; then
    docker run\
    -it \
    --rm \
    --name rentamovie \
    -v `pwd`:/opt/rentamovie/ \
    -w /opt/rentamovie/ \
    --network bridge \
    -e APP_DATABASE=':memory:' \
    rentamovie \
    sh tdd.sh
else
    docker run\
    -it \
    --rm \
    --name rentamovie \
    -v `pwd`:/opt/rentamovie/ \
    -w /opt/rentamovie/ \
    --network bridge \
    -p 8000:8000 \
    -e APP_DATABASE=test.db \
    rentamovie
fi
