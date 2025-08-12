#!/usr/bin/bash
redis-server /etc/redis/redis.conf &
cd /workspace/pytractions/traction-runner-webui
npm start
