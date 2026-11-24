"""Shared setup and hash-verified download helpers for workshop notebooks."""

import hashlib
import os
import urllib.request

import yaml

from economic_libraries.paths import PROJECT_ROOT


def setup_repo_root():
    """Change working directory to the repository root and return it."""
    os.chdir(PROJECT_ROOT)
    return PROJECT_ROOT


def fetch(key):
    """Return a local input path from downloads.yaml, downloading and hash-checking if needed."""
    setup_repo_root()
    inputs = yaml.safe_load((PROJECT_ROOT / "references/configs/downloads.yaml").read_text())
    spec = inputs[key]
    path = PROJECT_ROOT / spec["path"]
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        request = urllib.request.Request(spec["url"], headers={"User-Agent": "Mozilla/5.0"})
        path.write_bytes(urllib.request.urlopen(request, timeout=60).read())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != spec["sha256"]:
        raise ValueError(f"{path.name}: hash mismatch {digest}")
    return path
