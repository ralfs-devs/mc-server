# Minecraft Server

This repository contains a self-hosted Minecraft server deployment based on
Docker. The server application is downloaded from the official Mojang version
manifest at build time, so no prebuilt Minecraft image is used. World data and
configuration persist in a named Docker volume, and the container restarts
automatically after a crash. The project was developed for educational
purposes only.

## Table of Contents

- [Prerequisites](#prerequisites)
  - [First Start and Eula](#first-start-and-eula)
- [Quickstart](#quickstart)
- [Usage](#usage)
  - [Configuration](#configuration)
  - [Testing](#testing)
- [Project Structure](#project-structure)

## Prerequisites

To work with this repository you need the following tools installed on your machine:

- **Git** for cloning the repository
- **Docker** with the `docker compose` plugin for building and running the container
- (optional) **Python 3.12 or later** for running the test suite

### First Start and EULA

The server requires explicit acceptance of the [Minecraft EULA](https://www.minecraft.net/en-us/eula)
before it can run.  
The `entrypoint.sh` script automatically sets `eula=true` on first start.  
By deploying this server you declare that you accept the terms of the  
Minecraft End User License Agreement.

## Quickstart

1. Connect to your server via SSH

   ```bash
   ssh <your-vm>
   ```

2. Clone the repository

   ```bash
   git clone https://github.com/ralfs-devs/mc-server.git
   ```

3. Navigate into the project folder

   ```bash
   cd mc-server
   ```

4. Start the server

   ```bash
   docker compose up -d --build
   ```

5. Verify that the server is reachable

   ```bash
   python tests/test_reachability.py --host <vm-ip> --port 8888
   ```

   Alternatively open the multiplayer menu in your Minecraft Java client
   and connect to `<vm-ip>:8888`.

> **Warning**: The server starts with default values. Before exposing it to
> the internet, follow the [Usage](#usage) and
> [Configuration](#configuration) sections, especially the instructions for
> the `.env` file.

## Usage

This section explains how to configure and customize the server deployment.

### Configuration

The server accepts configuration via environment variables. Copy the example
environment file and adjust it to your needs:

```bash
cp example.env .env
```

Then restart the server:

```bash
docker compose up -d --build
```

Available environment variables:

| Variable | Description | Default |
| ---------- | ------------- | --------- |
| `EULA` | Accept the EULA (required) | `true` |
| `MAX_MEMORY` | Maximum memory allocation | `2G` |
| `MIN_MEMORY` | Minimum memory allocation | `1G` |
| `MOTD` | Message of the day | `A Minecraft Server` |
| `LEVEL_NAME` | World name | `world` |
| `SERVER_PORT` | Container port | `25565` |
| `HOST_PORT` | Host port mapping | `8888` |

> **Note**: Critical configuration like tokens, passwords, or sensitive
> information must not be stored in this repository. Use the `.env` file
> exclusively for such data.

### Testing

The test suite verifies reachability, persistence, and crash-recovery
behaviour. Run the tests against your deployed server:

1. Reachability test (connect from outside):

   ```bash
   python tests/test_reachability.py --host <vm-ip> --port 8888
   ```

2. Persistence test (configuration survives restart):

   ```bash
   DOCKER_HOST=ssh://<vm-alias> python tests/test_persistence.py
   ```

3. Crash-recovery test (container restarts after application failure):

   ```bash
   DOCKER_HOST=ssh://<vm-alias> python tests/test_crash_restart.py
   ```

Replace `<vm-ip>` with your server's public IP and `<vm-alias>` with your
SSH alias from `~/.ssh/config`. The Docker commands require that your SSH
key authenticates without password and that you have permission to run
Docker on the remote host.
