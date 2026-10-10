"""Crash and restart test for the Minecraft server."""

import subprocess
import sys
import time
from typing import Optional


def read_motd() -> str:
    """Read the current MOTD from the running container.

    Returns:
        str: The current MOTD value.
    """
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "mc-server",
            "grep",
            "^motd=",
            "/server/data/server.properties",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_container_status() -> Optional[str]:
    """Get the current status of the minecraft-server container.

    Returns:
        str | None: Container status (e.g., 'Up X seconds'), None if not found.
    """
    result = subprocess.run(
        [
            "docker",
            "ps",
            "--filter",
            "name=minecraft-server",
            "--format",
            "{{.Status}}",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    status = result.stdout.strip()
    return status if status else None


def get_restart_count() -> int:
    """Get the current restart count of the container.

    Returns:
        int: Number of restarts.
    """
    result = subprocess.run(
        ["docker", "inspect", "minecraft-server", "--format", "{{.RestartCount}}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return int(result.stdout.strip())


def crash_server() -> None:
    """Kill the Minecraft server process to simulate an application crash.

    Raises:
        subprocess.CalledProcessError: If the command fails.
    """
    subprocess.run(
        ["docker", "compose", "exec", "mc-server", "pkill", "-f", "server.jar"],
        check=True,
    )


def main() -> int:
    """Verify that the container restarts after a crash and data persists.

    Returns:
        int: Exit code, 0 on success, 1 on failure.
    """
    motd_before: str = read_motd()
    print(f"MOTD before crash: {motd_before}")

    restart_count_before: int = get_restart_count()
    print(f"Restart count before crash: {restart_count_before}")

    print("Triggering crash...")
    try:
        crash_server()
    except subprocess.CalledProcessError as exc:
        print(f"FAIL: could not crash server ({exc})")
        return 1

    print("Waiting for restart...")
    for _ in range(10):
        time.sleep(1)
        if get_restart_count() > restart_count_before:
            break
    restart_count_after: int = get_restart_count()
    print(f"Restart count after crash: {restart_count_after}")

    if restart_count_after <= restart_count_before:
        print("FAIL: container did not restart (restart count unchanged)")
        return 1
    status: Optional[str] = get_container_status()
    if not status or "Up" not in status:
        print(f"FAIL: container not running after crash (status: {status})")
        return 1

    print(f"Container status after restart: {status}")

    motd_after: str = read_motd()
    print(f"MOTD after restart:  {motd_after}")

    if motd_before == motd_after:
        print("PASS: container restarted and data persisted")
        return 0
    print("FAIL: data changed after crash-restart")
    return 1


if __name__ == "__main__":
    sys.exit(main())
