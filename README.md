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
  - [Lifecycle](#lifecycle)
- [Project Structure](#project-structure)

## Prerequisites

To work with this repository you need the following tools installed on your machine:

- **Git** for cloning the repository
- **Docker** with the `docker compose` plugin for building and running the container
- (optional) **Python 3.12 or later** for running the test suite

### First Start and EULA

The server requires explicit acceptance of the [Minecraft EULA](https://www.minecraft.net/en-us/eula)
before it can run.  
Acceptance is configured via the `.env` file (`EULA=true`).  
The `entrypoint.sh` script writes this value to `eula.txt` on startup.  
If `EULA=false` (default in `example.env`), the server will refuse to start.

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

4. Copy the example environment:

   ```bash
   cp example.env .env
   ```

5. Read the Minecraft [EULA](https://www.minecraft.net/en-us/eula) and accept it
   by setting `EULA=true` with the following command:

   > **Note**: Without acceptance, the server will not start.
   > **Warning**: Only set `EULA=true` if you agree to the terms of the EULA:

   ```bash
   sed -i 's/^EULA=false/EULA=true/' .env
   ```

6. Start the server

   ```bash
   docker compose up -d --build
   ```

7. Verify that the server is reachable

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

Available environment variables:

| Variable     | Description                       | Default in example.env |
| ------------ | --------------------------------- | ---------------------- |
| `EULA`       | Acceptance of the Minecraft EULA  | `false`                |
| `MAX_MEMORY` | Maximum heap size (`-Xmx`)        | `1G`                   |
| `MIN_MEMORY` | Initial heap size (`-Xms`)        | `512M`                 |
| `MOTD`       | Message of the day in server list | `Minecraft Server`     |
| `HOST_PORT`  | Minecraft server's public port    | `8888`                 |

> **Note**: Critical configuration like tokens, passwords, or sensitive
> information must not be stored in this repository. Use the `.env` file
> exclusively for such data.

### Lifecycle

The container uses the restart policy `unless-stopped`: it restarts
automatically after a crash or a VM reboot, but stays down once it is stopped
explicitly.

Stop the stack:

```bash
docker compose down
```

Restart it again:

```bash
docker compose up -d
```

World data and configuration survive a stop/start cycle because they are
stored persistently in the `mc-data` volume. Adding `-v` to the down command
destroys the volumes and all data with it:

```bash
# Careful: all user data will be lost.
docker compose down -v
```

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

## Project Structure

- `Dockerfile`: Builds the server image based on `eclipse-temurin:25-jre-alpine`,
  downloads the Minecraft server jar via the Mojang version manifest.
- `docker-compose.yaml`: Defines the `mc-server` service, port mapping
  (8888 → 25565), volume, and restart policy.
- `entrypoint.sh`: Accepts the EULA, sets the MOTD on first start, starts the JVM.
- `.dockerignore`: Reduces the build context to the files required in the image.
- `.gitignore`: Excludes irrelevant and sensitive files from version control.
- `example.env`: Template for the environment variables.
- `requirements.txt`: Python dependencies for the test suite and pre-commit hooks.
- `setup.cfg`: Flake8 configuration.
- `.pre-commit-config.yaml`: Pre-commit hooks (hadolint, yamllint,
  markdownlint-cli2, black, flake8).
- `.yamllint.yaml`: Yamllint configuration.
- `.github/workflows/lint.yml`: CI pipeline running the pre-commit hooks.
- `tests/`: Operator-facing test suite (reachability, persistence, crash recovery).
- `project_checklist_commented.pdf`: Completed project checklist confirming
  that all requirements from the DevSecOps course were fulfilled.
