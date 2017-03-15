from __future__ import division

import pytest
import numpy as np
from sklearn.dummy import DummyClassifier

from src.validation import *


@pytest.fixture
def clf():
    return DummyClassifier(strategy='uniform')


class TestDirichletResample(object):
    def test_grouping_numpy(self):
        n_classes = 3
        n_samples_per_class = 5
        y = np.repeat(range(n_classes), n_samples_per_class)
        X = np.concatenate([np.full((n_samples_per_class, 7), i)
                            for i in range(n_classes)])

        for _ in range(100):
            X_new, y_new = dirichlet_resample(X, y)
            assert np.all(X_new == y_new[:, np.newaxis])

            idx = np.random.choice(n_classes * n_samples_per_class, 100)
            X_new, y_new = dirichlet_resample(X[idx], y[idx])
            assert np.all(X_new == y_new[:, np.newaxis])
            assert len(X_new) == len(y_new) == len(idx)

    def test_grouping_pandas(self):
        n_classes = 3
        n_samples_per_class = 5
        n_samples = n_classes * n_samples_per_class
        idx = list(map(chr, range(65, 65 + n_samples)))
        y = pd.Series(np.repeat(range(n_classes), n_samples_per_class),
                      index=idx)
        X = np.concatenate([np.full((n_samples_per_class, 7), i)
                            for i in range(n_classes)])
        X = pd.DataFrame(X, index=idx)
        for _ in range(100):
            X_new, y_new = dirichlet_resample(X, y)
            assert (X_new.index == y_new.index).all()
            X_new = X_new.reset_index(drop=True)
            y_new = y_new.reset_index(drop=True)
            assert X_new.eq(y_new, axis=0).all().all()

            idx_new = np.random.choice(idx, 100)
            X_new, y_new = dirichlet_resample(X.loc[idx_new], y.loc[idx_new])
            assert len(X_new) == len(y_new) == len(idx_new)
            assert (X_new.index == y_new.index).all()
            X_new = X_new.reset_index(drop=True)
            y_new = y_new.reset_index(drop=True)
            assert X_new.eq(y_new, axis=0).all().all()

    @pytest.mark.parametrize('n_samples',[1, 5, 5.0, 10, 100])
    def test_n_samples(self, n_samples):
        n_classes = 3
        n_samples_per_class = 5
        y = np.repeat(range(n_classes), n_samples_per_class)
        X = np.concatenate([np.full((n_samples_per_class, 7), i)
                            for i in range(n_classes)])

        X_new, y_new = dirichlet_resample(X, y, n_samples)
        assert np.all(X_new == y_new[:, np.newaxis])
        assert len(X_new) == len(y_new) == n_samples

    def test_request_zero_samples(self):
        n_classes = 3
        n_samples_per_class = 5
        y = np.repeat(range(n_classes), n_samples_per_class)
        X = np.concatenate([np.full((n_samples_per_class, 7), i)
                            for i in range(n_classes)])

        X_new, y_new = dirichlet_resample(X, y, 0)
        assert np.all(X_new == y_new[:, np.newaxis])
        assert len(X_new) == len(y_new) == len(X) == len(y)

    def test_dirichlet(self):
        n_classes = 5
        y = np.repeat(range(n_classes), range(10, 20 * n_classes + 1, 20))
        X = np.ones((y.shape[0], 7))

        csmfs = []
        for _ in range(10000):
            X_new, y_new = dirichlet_resample(X, y)
            classes, counts = np.unique(y_new, return_counts=True)
            csmf = counts / counts.sum()

            # Handle unsampled classes. The final array must be square.
            if len(csmf) < n_classes:
                for i in set(range(n_classes)).difference(y_new):
                    csmf = list(csmf)
                    csmf.insert(i, 0)

            csmfs.append(csmf)

        csmfs = np.array(csmfs).mean(0)
        assert np.allclose(csmfs, 1 / n_classes, atol=0.005)


class TestPredictionAccuracy(object):
    pass


@pytest.mark.parametrize('ms_id', ['sss', 'holdout'])
def test_config_model_selector(ms_id):
    ms = config_model_selector(ms_id)
    assert hasattr(ms, 'split')


class TestOutOfSampleAccuracy(object):
    def test_selector_StratifiedShuffleSplit(self, clf):
        x = np.zeros((100, 5))
        y = np.tile(range(5), 20)
        g = np.array([int(i / 20) for i in range(100)])
        ms = config_model_selector('sss')
        out_of_sample_accuracy(x, y, clf, ms, groups=g)

    def test_selector_StratifiedShuffleSplit_splits(self, clf):
        x = np.zeros((100, 5))
        y = np.tile(range(5), 20)
        g = np.array([int(i / 20) for i in range(100)])
        n_splits = 5
        ms = config_model_selector('sss', n_splits=n_splits)
        results = out_of_sample_accuracy(x, y, clf, ms, groups=g)
        preds, csmf, ccc, accuracy = results
        assert len(accuracy) == n_splits

    def test_selector_LeavePGroupsOut(self, clf):
        x = np.zeros((100, 5))
        y = np.tile(range(5), 20)
        g = np.array([int(i / 20) for i in range(100)])
        ms = config_model_selector('holdout')
        out_of_sample_accuracy(x, y, clf, ms, groups=g)

    def test_selector_LeavePGroupsOut_splits(self, clf):
        x = np.zeros((100, 5))
        y = np.tile(range(5), 20)
        g = np.array([int(i / 20) for i in range(100)])
        ms = config_model_selector('holdout')
        results = out_of_sample_accuracy(x, y, clf, ms, groups=g)
        preds, csmf, ccc, accuracy = results
        assert len(accuracy) == len(np.unique(g))


def test_in_sample_accuracy(clf):
    x = np.zeros((100, 5))
    y = np.tile(range(5), 20)
    g = np.array([int(i / 20) for i in range(100)])
    ms = config_model_selector('sss')
    in_sample_accuracy(x, y, clf, ms, groups=g)
