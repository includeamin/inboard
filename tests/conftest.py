import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from _pytest.tmpdir import TempPathFactory
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from inboard import gunicorn_conf as gunicorn_conf_module
from inboard import logging_conf as logging_conf_module
from inboard.app import prestart as pre_start_module
from inboard.app.fastapibase.main import app as fastapi_app
from inboard.app.starlettebase.main import app as starlette_app


@pytest.fixture(scope="session")
def app_module_tmp_path(tmp_path_factory: TempPathFactory) -> Path:
    """Copy app modules to temporary directory to test custom app module paths."""
    tmp_dir = tmp_path_factory.mktemp("app")
    shutil.copytree(f"{Path(pre_start_module.__file__).parent}", f"{tmp_dir}/tmp_app")
    return tmp_dir


@pytest.fixture
def basic_auth(
    monkeypatch: MonkeyPatch,
    username: str = "test_username",
    password: str = "plunge-germane-tribal-pillar",
) -> tuple:
    """Set username and password for HTTP Basic Auth."""
    monkeypatch.setenv("BASIC_AUTH_USERNAME", username)
    monkeypatch.setenv("BASIC_AUTH_PASSWORD", password)
    assert os.getenv("BASIC_AUTH_USERNAME") == username
    assert os.getenv("BASIC_AUTH_PASSWORD") == password
    return username, password


@pytest.fixture(scope="session")
def clients() -> List[TestClient]:
    """Instantiate test client classes."""
    return [TestClient(fastapi_app), TestClient(starlette_app)]


@pytest.fixture
def gunicorn_conf_path(monkeypatch: MonkeyPatch) -> Path:
    """Set path to default Gunicorn configuration file."""
    path = Path(gunicorn_conf_module.__file__)
    monkeypatch.setenv("GUNICORN_CONF", str(path))
    assert os.getenv("GUNICORN_CONF") == str(path)
    return path


@pytest.fixture
def gunicorn_conf_path_tmp(tmp_path: Path) -> Path:
    """Copy gunicorn configuration file to custom temporary file."""
    tmp_file = shutil.copy(Path(gunicorn_conf_module.__file__), tmp_path)
    return Path(tmp_file)


@pytest.fixture
def logging_conf_dict(mocker: MockerFixture) -> Dict[str, Any]:
    """Load logging configuration dictionary from logging configuration module."""
    return mocker.patch.dict(logging_conf_module.LOGGING_CONFIG)


@pytest.fixture
def logging_conf_module_path(monkeypatch: MonkeyPatch) -> str:
    """Set module path to logging_conf.py."""
    path = "inboard.logging_conf"
    monkeypatch.setenv("LOGGING_CONF", path)
    assert os.getenv("LOGGING_CONF") == path
    return path


@pytest.fixture(scope="session")
def logging_conf_tmp_path(tmp_path_factory: TempPathFactory) -> Path:
    """Copy logging configuration module to custom temporary location."""
    tmp_dir = tmp_path_factory.mktemp("tmp_log")
    shutil.copy(Path(logging_conf_module.__file__), f"{tmp_dir}/tmp_log.py")
    return tmp_dir


@pytest.fixture(scope="session")
def logging_conf_tmp_path_no_dict(tmp_path_factory: TempPathFactory) -> Path:
    """Create temporary logging config file without logging config dict."""
    tmp_dir = tmp_path_factory.mktemp("tmp_log_no_dict")
    tmp_file = tmp_dir / "no_dict.py"
    with open(Path(tmp_file), "x") as f:
        f.write("print('Hello, World!')\n")
    return tmp_dir


@pytest.fixture(scope="session")
def logging_conf_tmp_path_incorrect_type(tmp_path_factory: TempPathFactory) -> Path:
    """Create temporary logging config file with incorrect LOGGING_CONFIG type."""
    tmp_dir = tmp_path_factory.mktemp("tmp_log_incorrect_type")
    tmp_file = tmp_dir / "incorrect_type.py"
    with open(Path(tmp_file), "x") as f:
        f.write("LOGGING_CONFIG: list = ['Hello', 'World']\n")
    return tmp_dir


@pytest.fixture
def mock_logger(mocker: MockerFixture) -> logging.Logger:
    """Mock the logger with pytest-mock and a pytest fixture.
    - https://github.com/pytest-dev/pytest-mock
    - https://docs.pytest.org/en/latest/fixture.html
    """
    logger = logging.getLogger()
    mocker.patch.object(logger, "debug")
    mocker.patch.object(logger, "error")
    mocker.patch.object(logger, "info")
    return logger


@pytest.fixture
def pre_start_script_tmp_py(tmp_path: Path) -> Path:
    """Copy pre-start script to custom temporary file."""
    tmp_file = shutil.copy(Path(pre_start_module.__file__), tmp_path)
    return Path(tmp_file)


@pytest.fixture
def pre_start_script_tmp_sh(tmp_path: Path) -> Path:
    """Create custom temporary pre-start shell script."""
    tmp_file = tmp_path / "prestart.sh"
    with open(Path(tmp_file), "x") as f:
        f.write('echo "Hello World, from a temporary pre-start shell script"\n')
    return Path(tmp_file)
