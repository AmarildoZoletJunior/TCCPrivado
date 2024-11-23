#!/bin/bash
set -e

envsubst < /app/config.ini > /app/config.ini.temp
mv /app/config.ini.temp /app/config.ini

exec "$@"