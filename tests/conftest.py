# pylint: disable=missing-docstring
from click.testing import CliRunner

import pytest


@pytest.fixture
def runner():
    yield CliRunner()
