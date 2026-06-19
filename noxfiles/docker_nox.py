"""Minimal docker nox sessions mirroring the fidesplus build/push approach:
build a local image, then push it tagged with the setuptools-scm version plus a
constant channel tag (rc / latest), exactly like fidesplus's push(slim) -- rc/prod."""

import os
import subprocess

import nox

# DockerHub repo, e.g. "galvana/gitflow-sandbox". Defaults from DOCKER_USER.
IMAGE = os.environ.get(
    "IMAGE_NAME", f"{os.environ.get('DOCKER_USER', 'local')}/gitflow-sandbox"
)


def _scm_version() -> str:
    """Derive the version from the git tag, like setuptools-scm does in fidesplus."""
    out = subprocess.run(
        ["python", "-m", "setuptools_scm"], capture_output=True, text=True
    )
    return out.stdout.strip() or "0.0.0"


@nox.session()
def build(session: nox.Session) -> None:
    """Build the (minimal) image locally as IMAGE:local."""
    session.run("docker", "build", "-t", f"{IMAGE}:local", ".", external=True)


@nox.session()
def push(session: nox.Session) -> None:
    """Push the built image. Channel via posarg: rc | prod | edge (default edge).

    - rc   -> IMAGE:<version>, IMAGE:rc
    - prod -> IMAGE:<version>, IMAGE:latest
    - edge -> IMAGE:edge
    """
    channel = session.posargs[0] if session.posargs else "edge"
    version = _scm_version()
    if channel == "prod":
        targets = [f"{IMAGE}:{version}", f"{IMAGE}:latest"]
    elif channel == "rc":
        targets = [f"{IMAGE}:{version}", f"{IMAGE}:rc"]
    else:
        targets = [f"{IMAGE}:edge"]

    for target in targets:
        session.run("docker", "tag", f"{IMAGE}:local", target, external=True)
        session.run("docker", "push", target, external=True)
        session.log(f"pushed {target}")
