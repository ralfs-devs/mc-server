"""Persistence test for the Minecraft server data volume."""

import subprocess
import sys

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


def compose(*args: str) -> subprocess.CompletedProcess:
    """Run a docker compose command.

    Args:
        *args (str): Arguments passed to docker compose.

    Returns:
        subprocess.CompletedProcess: The finished subprocess result.
    """
    return subprocess.run(["docker", "compose", *args], check=True)


def main() -> int:
    """Verify that volume data survives a restart cycle.

    Returns:
        int: Exit code, 0 on success, 1 on failure.
    """
    write_marker()
    print(f"Marker before restart: {read_marker()}")

    compose("down")
    compose("up", "-d")

    marker_after: str = read_marker()
    print(f"Marker after restart:  {marker_after}")

    if MARKER_TEXT == marker_after:
        print("PASS: volume data persisted across restart")
        return 0
    print("FAIL: marker lost or changed after restart")
    return 1


if __name__ == "__main__":
    sys.exit(main())
