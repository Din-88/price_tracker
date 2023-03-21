#!/bin/bash


# docker compose -f docker-compose.yml -f docker-compose_dev.yml --env-file=.env --env-file=.env.dev up --build

docker compose -f docker-compose.yml -f docker-compose_dev.yml --env-file=.env --env-file=.env.dev up
