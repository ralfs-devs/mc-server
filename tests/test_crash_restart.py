"""Crash and restart test for the Minecraft server."""

import subprocess
import sys
import time
from typing import Optional

MARKER_TEXT = "ralfs-devsecops-persistence-marker-2026"


def write_marker() -> None:
    """Write the marker file into the persistent data volume."""
    subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "mc-server",
            "sh",
            "-c",
            f"echo '{MARKER_TEXT}' > /server/data/persistence.marker",
        ],
        check=True,
    )


def read_marker() -> str:
    """Read the marker file from the persistent data volume.

    Returns:
        str: The stored marker content.
    """
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "mc-server",
            "cat",
            "/server/data/persistence.marker",
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
    write_marker()
    restart_count_before: int = get_restart_count()
    print(f"Restart count before crash: {restart_count_before}")
    marker_before: str = read_marker()
    print(f"Marker before crash:      {marker_before}")
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

    marker_after: str = read_marker()
    print(f"Marker after crash:      {marker_after}")
    if MARKER_TEXT != marker_after:
        print("FAIL: marker lost or changed after crash-restart")
        return 1

    print("PASS: container restarted and data persisted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
