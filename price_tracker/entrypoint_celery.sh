#!/bin/bash

export PATH=$PATH:/home/price_tracker/.local/bin


if [ "$ENVIRONMENT" == "prod" ]; then
  echo "LOAD Production Environment"
  exec celery --app api_tracker.workers worker \
              --beat \
              --scheduler django \
              --concurrency 1 -P solo \
              --uid=nobody --gid=nogroup \
              --loglevel=info
  echo "ny opeat xz"
elif [ "$ENVIRONMENT" == "dev" ]; then
  echo "LOAD Development Environment"
  exec celery --app api_tracker.workers worker \
              --beat \
              --scheduler django \
              --concurrency 1 -P solo \
              --uid=nobody --gid=nogroup \
              --loglevel=info
  echo "ny opeat xz"  
else
  echo "unknown environment"
  /bin/bash
fi


