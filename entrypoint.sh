#!/bin/sh
set -e

cd /server/data

echo "eula=${EULA:-true}" > eula.txt

if ! grep -q "^motd=" server.properties 2>/dev/null; then
    echo "motd=${MOTD:-Minecraft Server}" >> server.properties
fi

exec java -Xmx${MAX_MEMORY:-1G} -Xms${MIN_MEMORY:-512M} -jar /server/server.jar nogui
