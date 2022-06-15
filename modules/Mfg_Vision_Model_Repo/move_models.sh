#!/bin/bash

set -e

exec yes | cp -rf /models_temp/* /model_volume &
exec python3 /app/main.py 