import os

import numpy as np
import pandas as pd
import pytest

from smartva_ import SmartvaClassifier

needs_smartva_repo = pytest.mark.skipif(
    not os.path.exists(pytest.config.getoption("--smartva-repo")),
    reason='Cannot find Smartva repo'
)


@pytest.fixture(scope='module')
def clf_short(smartva_repo, module):
    return SmartvaClassifier(smartva_repo, module, short=True).fit()


@pytest.fixture(scope='module')
def clf_full(smartva_repo, module):
    return SmartvaClassifier(smartva_repo, module, short=False).fit()


@needs_smartva_repo
def test_full_fit(clf_full):
    assert isinstance(clf_full.tariffs_, pd.DataFrame)
    assert isinstance(clf_full.X_uniform_, np.ndarray)


@needs_smartva_repo
def test_short_fit(clf_short):
    assert isinstance(clf_short.tariffs_, pd.DataFrame)
    assert isinstance(clf_short.X_uniform_, np.ndarray)


@needs_smartva_repo
def test_fit_short_is_shorter(clf_full, clf_short):
    assert clf_full.symptoms_.shape[0] > clf_short.symptoms_.shape[0]
    assert clf_full.tariffs_.shape[1] > clf_short.tariffs_.shape[1]


@needs_smartva_repo
def test_full_predict(clf_full):
    arr = np.zeros((2, clf_full.tariffs_.shape[1]))
    df = pd.DataFrame(arr, columns=clf_full.symptoms_)
    clf_full.predict(arr)
    clf_full.predict(df)


@needs_smartva_repo
def test_short_predict(clf_short):
    arr = np.zeros((2, clf_short.tariffs_.shape[1]))
    df = pd.DataFrame(arr, columns=clf_short.symptoms_)
    clf_short.predict(arr)
    clf_short.predict(df)
