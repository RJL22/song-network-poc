import os
import subprocess
import sys
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]


def run_import(cwd: Path, extra_env: dict[str, str] | None = None):
    env = os.environ.copy()
    env.update({"DATABASE_URL": "sqlite://", "JWT_SECRET_KEY": "test-secret"})
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [
            sys.executable,
            "-c",
            "from app.core.security import create_access_token, decode_access_token; token=create_access_token(42); assert decode_access_token(token) == 42",
        ],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )


def test_jwt_works_from_repository_root():
    result = run_import(BACKEND.parent, {"PYTHONPATH": str(BACKEND)})
    assert result.returncode == 0, result.stderr


def test_jwt_works_from_backend_directory():
    result = run_import(BACKEND)
    assert result.returncode == 0, result.stderr


def test_missing_secret_fails_with_clear_configuration_error():
    result = run_import(BACKEND, {"JWT_SECRET_KEY": ""})
    assert result.returncode != 0
    assert "JWT_SECRET_KEY is not configured" in result.stderr
