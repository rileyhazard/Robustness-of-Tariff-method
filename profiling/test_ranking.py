import pytest
import numpy as np


@pytest.fixture
def data():
    n_causes = 46
    n_train = 7850   # Actual size of PHMRC training data
    n_test = 10_000
    X_test = np.random.randint(200, size=(n_test, n_causes)) * .5
    X_train = np.sort(np.random.randint(200, size=(n_train, n_causes)) * .5,
                      axis=0)
    return X_test, X_train


def rank_samples(X_test, X_train):
    """Determine rank of test samples within training data

    Args:
        X_test (array-like): samples by causes matrix of tariff scores
        X_train (array-like): samples by causes matrix of tariff scores

    Returns:
        ranked (np.array): samples by causes matrix of ranks within the
            training data for each sample in the test data
    """
    X_test_3d = X_test[:, :, None]
    X_train_3d = X_train.T[None, :, :]

    lower = np.apply_along_axis(np.sum, 2, X_test_3d < X_train_3d)
    higher = np.apply_along_axis(np.sum, 2, X_test_3d > X_train_3d)

    return (lower + (X_train.shape[0] - higher)) / 2 + 0.5


def rank_samples_better(X_test, X_train):
    n_causes = X_train.shape[1]
    lower = np.concatenate([
        np.searchsorted(X_train[:, i], X_test[:, i], 'left')[:, None]
        for i in range(n_causes)], 1)
    higher = np.concatenate([
        np.searchsorted(X_train[:, i], X_test[:, i], 'right')[:, None]
        for i in range(n_causes)], 1)
    return X_train.shape[0] - (lower + higher) / 2 + 0.5


def test_regression(data):
    arr1 = rank_samples(*data)
    arr2 = rank_samples_better(*data)
    assert (arr1 == arr2).all()


if __name__ == '__main__':
    X_test, X_train = data()
    print('Testing on {} observations'.format(X_test.shape[0]))
    # rank_samples(X_test, X_train)
    rank_samples_better(X_test, X_train)
