"""Download and start Lavalink server."""

import subprocess
import sys
import urllib.request
from pathlib import Path

LAVALINK_URL = (
    "https://github.com/lavalink-devs/Lavalink/releases/download/4.0.8/Lavalink.jar"
)


def download_lavalink() -> Path:
    """Download Lavalink.jar if it does not exist."""
    base_dir = Path(__file__).parent
    jar_path = base_dir / "Lavalink.jar"

    if jar_path.exists():
        print(f"Found existing Lavalink jar at {jar_path}")
        return jar_path

    print("Downloading Lavalink...")
    try:
        urllib.request.urlretrieve(LAVALINK_URL, jar_path)
        print(f"Downloaded Lavalink to {jar_path}")
    except Exception as exc:
        print(f"Failed to download Lavalink: {exc}")
        print(f"Please download manually from: {LAVALINK_URL}")
        sys.exit(1)

    return jar_path


def start_lavalink() -> None:
    """Start the Lavalink server."""
    jar_path = download_lavalink()
    base_dir = Path(__file__).parent

    cmd = ["java", "-jar", str(jar_path)]
    print(f"Starting Lavalink: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=base_dir)


if __name__ == "__main__":
    start_lavalink()
