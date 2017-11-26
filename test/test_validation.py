import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier

from tariff2.validation import *


def test_dirichlet_resample_seed():
    arr = np.random.choice(np.arange(13), 100)
    rs = np.random.RandomState(2301598121)
    state = rs.get_state()

    samples = []
    for _ in range(5):
        rs.set_state(state)
        samples.append(dirichlet_resample(arr, random_state=rs))
    assert all((sample == samples[0]).all() for sample in samples)


def test_dirichlet_resample_is_dirichlet():
    rs = np.random.RandomState(42)
    choices = 13
    n_samples = 100
    arr = rs.choice(np.arange(choices), n_samples)

    samples = []
    for _ in range(30):
        idx = dirichlet_resample(arr, random_state=rs)

        # Handle unsampled classes. The final array must be square.
        counts = dict(zip(*np.unique(arr[idx], return_counts=True)))
        samples.append([counts.get(i, 0) / n_samples for i in range(choices)])

    observed = np.array(samples).mean()
    expected = 1 / choices
    assert np.allclose(expected, observed, atol=0.00001)


@pytest.mark.parametrize('n_samples', [1, 5, 5.0, 10, 100])
def test_dirichlet_resample_n_samples(n_samples):
    arr = np.random.choice(7, 113)
    resampled = dirichlet_resample(arr, n_samples)
    assert resampled.shape[0] == n_samples


def test_dirichlet_resample_zero_samples():
    arr = np.random.choice(7, 113)
    resampled = dirichlet_resample(arr, 0)
    assert resampled.shape[0] == arr.shape[0]


def test_dirichlet_resample_string_array():
    n_samples = 13
    arr = np.random.choice(['a', 'b', 'c'], n_samples)
    resampled = dirichlet_resample(arr)
    assert resampled.shape[0] == n_samples
    assert resampled.dtype == np.int64


def test_dirichlet_resample_series():
    n_samples = 17
    ser = pd.Series(np.random.choice(7, n_samples),
                    list(map(chr, range(65, 65 + n_samples))))
    resampled = dirichlet_resample(ser)
    assert isinstance(resampled, np.ndarray)
    assert resampled.shape[0] == n_samples
    assert resampled.dtype == np.int64


@pytest.mark.parametrize('n_samples', [1, 5, 5.0, 10, 100])
def test_dirichlet_resample_X_y_n_samples(n_samples):
    X = np.ones((int(n_samples), 17))
    y = np.ones(int(n_samples))

    X_new, y_new = dirichlet_resample_X_y(X, y, n_samples)
    assert X_new.shape[0] == y_new.shape[0] == n_samples


def test_dirichlet_resample_X_y_zero_samples():
    n_samples = 13
    X = np.ones((n_samples, 17))
    y = np.ones(n_samples)

    X_new, y_new = dirichlet_resample_X_y(X, y, 0)
    assert np.all(X_new == y_new[:, np.newaxis])
    assert X_new.shape[0] == y_new.shape[0] == X.shape[0] == y.shape[0]


def test_dirichlet_resample_X_y_seed():
    n_samples = 113
    X = np.random.choice([0, 1], (n_samples, 17))
    y = np.random.choice(np.arange(13), n_samples)
    rs = np.random.RandomState(2301598121)
    state = rs.get_state()

    Xs, ys = [], []
    for _ in range(5):
        rs.set_state(state)
        X_, y_ = dirichlet_resample_X_y(X, y, random_state=rs)
        Xs.append(X_)
        ys.append(y_)
    assert all((X_ == Xs[0]).all() for X_ in Xs)
    assert all((y_ == ys[0]).all() for y_ in ys)


def test_dirichlet_resample_X_y_string_y():
    n_samples = 13
    X = np.ones((n_samples, 17))
    y = np.random.choice(['a', 'b', 'c'], n_samples)
    X_new, y_new = dirichlet_resample_X_y(X, y)
    assert X_new.shape[0] == y_new.shape[0] == X.shape[0] == y.shape[0]


def test_dirichlet_resample_X_y_grouping_numpy():
    y = np.repeat(np.arange(3), 13)
    X = np.repeat(y[:, np.newaxis], 7, 1)

    for _ in range(100):
        X_new, y_new = dirichlet_resample_X_y(X, y)
        assert np.all(X_new == y_new[:, np.newaxis])


def test_dirichlet_resample_X_y_grouping_pandas():
    n_samples = 7
    n_reps = 3
    idx = list(map(chr, range(65, 65 + n_samples * n_reps)))
    y = pd.Series(np.repeat(np.arange(n_reps), n_samples), index=idx)
    X = pd.DataFrame(np.repeat(y.values[:, np.newaxis], 7, 1), index=idx)

    for _ in range(100):
        X_new, y_new = dirichlet_resample_X_y(X, y)
        assert (X_new.index == y_new.index).all()
        X_new = X_new.reset_index(drop=True)
        y_new = y_new.reset_index(drop=True)
        assert X_new.eq(y_new, axis=0).all().all()


def test_RandomClassifier():
    n_samples = 97
    X = np.ones((n_samples, 3))
    clf = RandomClassifier().fit(X, np.ones(n_samples))
    y_pred, csmf_pred = clf.predict(X)
    assert isinstance(y_pred, pd.Series)
    assert isinstance(csmf_pred, pd.Series)


def test_RandomClassifier_predict_pandas():
    n_samples = 17
    idx = list(map(chr, range(65, 65 + n_samples)))
    X = pd.DataFrame(np.ones((n_samples, 3)), index=idx)
    clf = RandomClassifier().fit(X, np.ones(n_samples))
    y_pred, csmf_pred = clf.predict(X)
    assert isinstance(y_pred, pd.Series)
    assert (X.index == y_pred.index).all()
    assert isinstance(csmf_pred, pd.Series)
