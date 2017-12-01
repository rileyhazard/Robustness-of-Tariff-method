import os
import sys

import pytest


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

SMARTVA_REPO = os.path.join(os.path.dirname(REPO), 'smartva')


def pytest_addoption(parser):
    parser.addoption("--smartva-repo", default=SMARTVA_REPO)


@pytest.fixture(scope='session')
def smartva_repo(request):
    return request.config.getoption('--smartva-repo')


@pytest.fixture(params=['adult', 'child', 'neonate'], scope='module')
def module(request):
    return request.param
