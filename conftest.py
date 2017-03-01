import os

import pytest

SMARTVA_REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            '..', '..', 'smartva')


def pytest_addoption(parser):
    parser.addoption("--smartva-repo", default=SMARTVA_REPO)


@pytest.fixture(scope='session')
def smartva_repo(request):
    return request.config.getoption('--smartva-repo')


@pytest.fixture(params=['adult', 'child', 'neonate'], scope='module')
def module(request):
    return request.param


@pytest.fixture
def yml_adult_cause_num_to_letter(tmpdir):
    data = """
adult:
  cause:
    1: 'A'
    2: 'B'
    3: 'C'
    4: 'D'
    5: 'E'
"""
    file_ = tmpdir.join('adult_cause_num_to_letter.yml')
    file_.write(data)
    return file_.strpath


@pytest.fixture
def yml_child_cause_num_to_letter(tmpdir):
    data = """
child:
  cause:
    1: 'A'
    2: 'B'
    3: 'C'
    4: 'D'
    5: 'E'
"""
    file_ = tmpdir.join('child_cause_num_to_letter.yml')
    file_.write(data)
    return file_.strpath
