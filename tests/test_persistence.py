"""Persistence test for the Minecraft server configuration."""

import subprocess
import sys

def read_motd() -> str:
    """Read the current MOTD from the running container.

    Returns:
        str: The current MOTD value.
    """
    result = subprocess.run(
        ["docker", "compose", "exec", "-T", "mc-server",
         "grep", "^motd=", "/server/data/server.properties"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()

def compose(*args: str) -> subprocess.CompletedProcess:
    """Run a docker compose command.

    Args:
        *args (str): Arguments passed to docker compose.

    Returns:
        subprocess.CompletedProcess: The finished subprocess result.
    """
    return subprocess.run(["docker", "compose", *args], check=True)

def main() -> int:
    """Verify that configuration survives a restart cycle.

    Returns:
        int: Exit code, 0 on success, 1 on failure.
    """
    motd_before: str = read_motd()
    print(f"MOTD before restart: {motd_before}")

    compose("down")
    compose("up", "-d")

    motd_after: str = read_motd()
    print(f"MOTD after restart:  {motd_after}")

    if motd_before == motd_after:
        print("PASS: configuration persisted across restart")
        return 0
    print("FAIL: configuration changed after restart")
    return 1

if __name__ == "__main__":
    sys.exit(main())