from pathlib import Path


def cleanup_out_dir(d: Path):
    if not d.exists():
        return

    for f in d.rglob("*"):
        if f.is_file():
            f.unlink()
