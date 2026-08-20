import os
import subprocess


VM_PATH = os.path.join(
    os.path.dirname(__file__),
    "vm",
    "botGuard.js",
)


def generate_po_token(video_id: str) -> str:
    """Generate a poToken using botGuard."""
    import nodejs_wheel.executable

    node_dir = nodejs_wheel.executable.ROOT_DIR
    node_path = os.path.join(
        node_dir,
        "node.exe" if os.name == "nt" else "bin/node",
    )

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
