import os

from memory_profiler import profile
import numpy as np
import pytest


@pytest.fixture
def data():
    n_causes = 50
    n_symptoms = 300
    n_obs = int(os.environ.get('N_OBS', 1000))
    tariffs = np.random.randint(0, 200, (n_causes, n_symptoms)) * .5
    X = np.random.choice([0, 1], (n_obs, n_symptoms), p=(.8, .2))
    return X, tariffs


@profile
def score_samples(X, tariffs):
    return np.sum(X[:, :, None] * tariffs.T[None, :, :], 1)


@profile
def score_samples_better(X, tariffs):
    return np.inner(X[:, None, :], tariffs[None, :, :])[:, 0, 0, :]


def test_regression(data):
    arr1 = score_samples(*data)
    arr2 = score_samples_better(*data)
    assert (arr1 == arr2).all()


if __name__ == '__main__':
    X, tariffs = data()
    print('Testing on {} observations'.format(X.shape[0]))
    score_samples(X, tariffs)
    score_samples_better(X, tariffs)
