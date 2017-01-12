import numpy as np
import pandas as pd
import pytest
from sklearn.utils.estimator_checks import check_estimator

from src.tariff import *


def random_ones_zeros(shape):
    return np.vectorize(round)(np.random.random(shape))


@pytest.mark.skip
def test_sklearn_clf():
    check_estimator(TariffClassifier)


class TestTariffFromEndorsments(object):
    def test_half_negative(self):
        """
        The median is subtracted from each element and it is divided by
        the IQR. For series with even number of elements and no repeat
        values, half should be negative and half should be positive
        """
        clf = TariffClassifier()
        s = pd.Series(range(10))
        tariffs_j = clf.tariff_from_endorsements(s)
        assert len(tariffs_j[tariffs_j < 0]) == 5
        assert len(tariffs_j[tariffs_j > 0]) == 5

    def test_zero_iqr(self):
        clf = TariffClassifier()
        s = pd.Series([0] * 9 + [1])
        tariffs = clf.tariff_from_endorsements(s)
        assert tariffs.tolist() == [0] * 9 + [1000]


class TestCalcTariffs(object):
    def test_array_input(self):
        X = random_ones_zeros((100, 10))
        y = np.random.choice(5, 100)
        clf = TariffClassifier()
        tariffs = clf.calc_tariffs(X, y)
        assert isinstance(tariffs, pd.DataFrame)
        assert set(tariffs.index) == set(y)
        assert tariffs.columns.tolist() == range(10)

    def test_dataframe_input(self):
        X = pd.DataFrame(random_ones_zeros((100, 10)),
                         columns=map(chr, range(65, 75)))
        y = np.random.choice(5, 100)
        clf = TariffClassifier()
        tariffs = clf.calc_tariffs(X, y)
        assert isinstance(tariffs, pd.DataFrame)
        assert set(tariffs.index) == set(y)
        assert np.all(tariffs.columns == X.columns)


class TestCalcInsignificantTariffs(object):
    def test_array_input(self):
        X = random_ones_zeros((100, 10))
        y = np.random.choice(5, 100)
        clf = TariffClassifier()
        insignif = clf.calc_insignificant_tariffs(X, y, n=5)
        assert isinstance(insignif, pd.DataFrame)
        assert set(insignif.index) == set(y)
        assert insignif.columns.tolist() == range(10)
        assert insignif.values.dtype.type == np.bool_

    def test_dataframe_input(self):
        X = pd.DataFrame(random_ones_zeros((100, 10)),
                         columns=map(chr, range(65, 75)))
        y = np.random.choice(5, 100)
        clf = TariffClassifier()
        insignif = clf.calc_insignificant_tariffs(X, y, n=5)
        assert isinstance(insignif, pd.DataFrame)
        assert set(insignif.index) == set(y)
        assert np.all(insignif.columns == X.columns)
        assert insignif.values.dtype.type == np.bool_

    def test_string_causes(self):
        X = pd.DataFrame(random_ones_zeros((100, 10)),
                         columns=map(chr, range(65, 75)))
        y = np.random.choice(map(chr, range(65, 70)), 100)
        clf = TariffClassifier()
        insignif = clf.calc_insignificant_tariffs(X, y, n=5)
        assert isinstance(insignif, pd.DataFrame)
        assert set(insignif.index) == set(y)
        assert np.all(insignif.columns == X.columns)
        assert insignif.values.dtype.type == np.bool_


def test_round_tariffs():
    tariffs = pd.DataFrame([[0, .7, 1.1],
                            [-.3, .5, .66666]])
    clf = TariffClassifier()
    rounded = clf.round_tariffs(tariffs, 0.25)
    assert np.all(rounded == np.array([[0, .75, 1],
                                       [-.25, .5, .75]]))


def test_remove_spurious_associations():
    tariffs = pd.DataFrame(np.random.random((4, 5)))
    spurious = {
        1: [1, 2],
        2: [4]
    }
    clf = TariffClassifier()
    valid = clf.remove_spurious_associations(tariffs, spurious)
    assert valid.loc[1, 1] == valid.loc[1, 2] == valid.loc[2, 4] == 0
    assert np.all(tariffs.loc[0] == valid.loc[0])
    assert np.all(tariffs.loc[1, 0] == valid.loc[1, 0])
    assert np.all(tariffs.loc[1, 3:] == valid.loc[1, 3:])
    assert np.all(tariffs.loc[2, 0:3] == valid.loc[2, 0:3])
    assert np.all(tariffs.loc[3] == valid.loc[3])


class TestKeepTopSymptoms(object):
    def test_zeros_tariff(self):
        keep = 10
        df = pd.DataFrame([range(5, 16)])
        clf = TariffClassifier()
        only_top = clf.keep_top_symptoms(df, keep)
        assert only_top.iloc[0, 0] == 0
        assert np.all(only_top.iloc[0, 1:].values == np.arange(6, 16))
        assert np.sum(only_top.iloc[0] > 0) == keep

    def test_short_series(self):
        df = pd.DataFrame([range(5, 16)])
        clf = TariffClassifier()
        only_top = clf.keep_top_symptoms(df, 20)
        assert np.all((only_top == df))

    def test_large_negatives(self):
        keep = 10
        large_abs = range(-10, -5) + range(5, 10)
        df = pd.DataFrame([large_abs + [1]])
        clf = TariffClassifier()
        only_top = clf.keep_top_symptoms(df, keep)
        assert only_top.iloc[0, -1] == 0
        assert np.all(only_top.iloc[0, :-1].values == np.asarray(large_abs))
        assert np.sum(only_top.iloc[0].abs() > 0) == keep


def test_score_samples():
    clf = TariffClassifier()
    # 4 samples by 4 predictors
    X = np.array([[0, 0, 0, 1],
                  [1, 0, 1, 0],
                  [1, 1, 0, 0],
                  [0, 0, 0, 0]])
    # 2 causes by 4 predictors
    tariffs = np.array([[7, 5, 0, 1],
                        [1, 3, 7, 9]])
    # 4 samples by 2 causes
    actual = np.array([[1, 9],
                       [7, 8],
                       [12, 4],
                       [0, 0]])
    scored = clf.score_samples(X, tariffs)
    assert np.all(scored == actual)


def test_generate_uniform_list():
    clf = TariffClassifier()
    n = 100
    symps = 10
    causes = 5
    n_resamp = 50
    n_out = n_resamp * causes
    X = random_ones_zeros((n, symps))
    y = np.random.choice(range(causes), n)
    tariffs = np.random.random((causes, symps))
    X_uniform, y_uniform = clf.generate_uniform_list(X, y, tariffs, n=n_resamp)
    assert X_uniform.shape == (n_out, causes)


def test_rank_samples():
    clf = TariffClassifier()
    X = np.array([[0, 0],  # lowest score (rank=len(uniform))
                  [3, 3],
                  [7, 7],
                  [11, 11]])  # higher score than any training data (rank=0)
    uniform = np.array([[0, 4],
                        [2, 5],
                        [4, 6],
                        [6, 7],
                        [8, 8],
                        [10, 9]])
    actual = np.array([[6, 6],
                       [4, 6],
                       [2, 3],
                       [0, 0]])
    ranked = clf.rank_samples(X, uniform)
    assert np.all(ranked == actual)


def test_get_undetermined_proportions():
    clf = TariffClassifier(bootstraps=10)
    X = random_ones_zeros((100, 10))
    y = np.random.choice(range(5), 100)
    clf.fit(X, y)
    csmf = clf.get_undetermined_proportions()
    assert np.allclose(csmf.sum(), 1)


def test_redsitribution():
    csmf = pd.Series(np.random.dirichlet(np.ones(7)),
                     index=range(6) + [np.nan])
    prop = pd.Series(np.random.dirichlet(np.ones(6)))
    clf = TariffClassifier()
    csmf_new = clf.redistribution(csmf, prop)
    assert np.allclose(csmf_new.sum(), 1)


class TestFit(object):
    def test_returns_self(self):
        clf = TariffClassifier(bootstraps=10)
        X = random_ones_zeros((100, 10))
        y = np.random.choice(range(5), 100)
        ret = clf.fit(X, y)
        assert ret is clf


class TestPredict(object):
    def test_returns_series(self):
        clf = TariffClassifier(bootstraps=10)
        X = random_ones_zeros((100, 10))
        y = np.random.choice(range(5), 100)
        pred = clf.fit(X, y).predict(X)
        assert isinstance(pred, pd.Series)

    def test_no_nulls(self):
        clf = TariffClassifier(bootstraps=10)
        X = np.zeros((100, 10))
        y = np.random.choice(range(5), 100)
        pred = clf.fit(X, y).predict(X)
        assert not pred.isnull().sum()
