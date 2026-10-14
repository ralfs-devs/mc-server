FROM eclipse-temurin:25-jre-alpine
SHELL ["/bin/ash", "-o", "pipefail", "-c"]

WORKDIR /server

RUN apk add --no-cache curl=8.22.0-r0 jq=1.8.2-r0

ENV MAX_MEMORY=1G
ENV MIN_MEMORY=512M
ENV MOTD="Minecraft Server"

RUN MANIFEST_URL=https://piston-meta.mojang.com/mc/game/version_manifest_v2.json && VERSION=$(curl -sL "$MANIFEST_URL" | jq -r '.latest.release') && VERSION_URL=$(curl -sL "$MANIFEST_URL" | jq -r --arg v "$VERSION" '.versions[] | select(.id==$v) | .url') && curl -sL "$VERSION_URL" | jq -r '.downloads.server.url' | xargs curl -sLo /server/server.jar

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["start"]
