"""Reachability test for the Minecraft server."""

import argparse
import asyncio
import sys

from mcstatus import JavaServer


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments containing host, port, and timeout.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8888, help="Server port")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout in seconds")
    return parser.parse_args()


async def check(host, port, timeout) -> int:
    """Query the Minecraft server status.

    Args:
        host (str): Server hostname or IP.
        port (int): Server port.
        timeout (float): Timeout in seconds.

    Returns:
        int: Exit code, 0 on success, 1 on failure.
    """
    server = await JavaServer.async_lookup(f"{host}:{port}", timeout=timeout)
    status = await server.async_status()
    print(f"Version:  {status.version.name}")
    print(f"Players:  {status.players.online}/{status.players.max}")
    print(f"MOTD:     {status.motd.raw}")
    print(f"Latency:  {status.latency:.0f} ms")
    return 0


if __name__ == "__main__":
    args = parse_args()
    try:
        sys.exit(asyncio.run(check(args.host, args.port, args.timeout)))
    except OSError as exc:
        print(f"FAIL: could not reach {args.host}:{args.port} ({exc})", file=sys.stderr)
        sys.exit(1)
