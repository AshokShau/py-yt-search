import os
import shutil
import subprocess
from typing import Optional


VM_PATH = os.path.join(
    os.path.dirname(__file__),
    "vm",
    "botGuard.js",
)


def _get_node_executable() -> Optional[str]:
    try:
        import nodejs_wheel.executable  # type: ignore[import-not-found]

        node_dir = nodejs_wheel.executable.ROOT_DIR
        node_path = os.path.join(
            node_dir,
            "node.exe" if os.name == "nt" else "bin/node",
        )
        if os.path.exists(node_path):
            return node_path
    except (ImportError, AttributeError):
        pass

    return shutil.which("node")


def generate_po_token(video_id: str) -> str:
    """Generate a poToken using botGuard."""
    node_path = _get_node_executable()
    if not node_path:
        raise RuntimeError("Node.js executable not found.")

    try:
        result = subprocess.check_output(
            (node_path, VM_PATH, video_id),
            stderr=subprocess.PIPE,
        )
        return result.decode().strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to execute botGuard.js: {e.stderr.decode().strip()}"
        ) from e
