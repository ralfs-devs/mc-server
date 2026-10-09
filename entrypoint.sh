#!/bin/sh
set -e

cd /server/data

echo "eula=${EULA:-true}" > eula.txt

exec java -Xmx${MAX_MEMORY} -Xms${MIN_MEMORY} -jar /server/server.jar nogui
