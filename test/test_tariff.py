import numpy as np
import pandas as pd
import pytest

from src.tariff import *


def random_ones_zeros(shape):
    return np.vectorize(round)(np.random.random(shape))


def test_tariffs_from_endorsemets():
    arr = np.arange(0, 11) / 10
    expected = np.array([-1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1])

    tariffs = tariffs_from_endorsements(arr)
    assert np.allclose(tariffs, expected)

    arr = pd.Series(arr)
    tariffs = tariffs_from_endorsements(arr)
    assert np.allclose(tariffs, expected)


def test_tariffs_from_endorsemets_zero_iqr():
    arr = np.zeros(10)
    arr[3] = 1
    expected = np.zeros(10)
    expected[3] = 1000

    tariffs = tariffs_from_endorsements(arr)
    assert (tariffs == expected).all()

    ser = pd.Series(arr)
    tariffs = tariffs_from_endorsements(ser)
    assert (tariffs == expected).all()


def test_calc_tariffs_shape():
    n_causes = 5
    n_symptoms = 10
    n_samples = 100

    X = random_ones_zeros((n_samples, n_symptoms))
    y = np.random.choice(n_causes, n_samples)

    tariffs = calc_tariffs(X, y)
    assert isinstance(tariffs, np.ndarray)
    assert tariffs.shape == (n_causes, n_symptoms)

    symptoms = list(map(chr, range(65, 65 + n_symptoms)))
    X = pd.DataFrame(X, columns=symptoms)

    tariffs_df = calc_tariffs(X, y)
    assert isinstance(tariffs_df, pd.DataFrame)
    assert (tariffs_df.index == np.sort(np.unique(y))).all()
    assert (tariffs_df.columns == symptoms).all()
    assert (tariffs_df == tariffs).all().all()


def test_calc_tariffs_one_symp_per_cause():
    n_causes = 10
    n_samples_per_cause = 100

    X = np.repeat(np.eye(n_causes), n_samples_per_cause, 0)
    y = np.repeat(np.arange(n_causes), n_samples_per_cause)

    expected = np.eye(n_causes) * 1000

    tariffs = calc_tariffs(X, y)
    assert (tariffs == expected).all()


def test_bootstrap_endorsements_by_cause():
    assert False


def test_calc_insignificant_tariffs_shape():
    n_causes = 5
    n_symptoms = 10
    n_samples = 100
    n_bootstraps = 5

    X = random_ones_zeros((n_samples, n_symptoms))
    y = np.random.choice(n_causes, 100)

    insignif = calc_insignificant_tariffs(X, y, bootstraps=n_bootstraps)

    assert isinstance(insignif, np.ndarray)
    assert insignif.shape == (n_causes, n_symptoms)
    assert insignif.dtype.type == np.bool_

    symptoms = list(map(chr, range(65, 65 + n_symptoms)))
    X = pd.DataFrame(X, columns=symptoms)

    insignif = calc_insignificant_tariffs(X, y, bootstraps=n_bootstraps)
    assert isinstance(insignif, pd.DataFrame)
    assert (insignif.index == np.sort(np.unique(y))).all()
    assert (insignif.columns == symptoms).all()
    assert insignif.values.dtype.type == np.bool_


# TODO: When generating matrices of symptom endorsements for insiginficance
# test, since X is randomly generated it's unlike that any tariffs are
# significant. It is likely that the results are the trivial case where
# there are no sigificant tariffs on either matrix. Draw endorsements
# non-randomly and the sum signficances is know a priori


def test_calc_insignificant_tariffs_seed():
    n_causes = 5
    n_symptoms = 10
    n_samples = 100
    n_bootstraps = 50

    X = random_ones_zeros((n_samples, n_symptoms))
    y = np.random.choice(n_causes, 100)

    draws = list()
    for _ in range(7):
        rs = np.random.RandomState(2301598121)
        insignif = calc_insignificant_tariffs(X, y, bootstraps=n_bootstraps,
                                              random_state=rs)
        draws.append(insignif)

    assert np.all([(draws[0] == arr).all() for arr in draws])


def test_calc_insignificant_tariffs_ui():
    n_causes = 5
    n_symptoms = 10
    n_samples = 100
    n_bootstraps = 50
    seed = 2301598121

    X = random_ones_zeros((n_samples, n_symptoms))
    y = np.random.choice(n_causes, 100)

    rs = np.random.RandomState(seed)
    many_insignif = calc_insignificant_tariffs(X, y, bootstraps=n_bootstraps,
                                               random_state=rs, ui=(0.5, 99.5))

    rs = np.random.RandomState(seed)
    few_insignif = calc_insignificant_tariffs(X, y, bootstraps=n_bootstraps,
                                              random_state=rs, ui=(25, 75))
    assert np.all(many_insignif[few_insignif])

    assert np.sum(many_insignif) >= np.sum(few_insignif)


def test_calc_insignificant_tariffs_ui_order():
    n_causes = 5
    n_symptoms = 10
    n_samples = 100
    n_bootstraps = 10
    seed = 2301598121

    X = random_ones_zeros((n_samples, n_symptoms))
    y = np.random.choice(n_causes, 100)

    rs = np.random.RandomState(seed)
    ascending = calc_insignificant_tariffs(X, y, bootstraps=n_bootstraps,
                                           random_state=rs, ui=(2, 98))

    rs = np.random.RandomState(seed)
    descending = calc_insignificant_tariffs(X, y, bootstraps=n_bootstraps,
                                            random_state=rs, ui=(98, 2))
    assert np.all(ascending == descending)


def test_round_tariffs():
    tariffs = np.array([[0, .7, 1.1],
                        [-.3, .5, .66666]])

    expected = np.array([[0, .75, 1],
                         [-.25, .5, .75]])

    rounded = round_tariffs(tariffs, 0.25)
    assert isinstance(rounded, np.ndarray)
    assert (rounded == expected).all()

    idx = np.array(['A', 'B'])
    cols = np.array(['a', 'b', 'c'])
    tariffs = pd.DataFrame(tariffs, idx, cols)
    rounded = round_tariffs(tariffs, 0.25)
    assert isinstance(rounded, pd.DataFrame)
    assert (rounded == expected).all().all()
    assert (rounded.index == idx).all()
    assert (rounded.columns == cols).all()


def test_remove_spurious_associations():
    tariffs = np.random.random((4, 5))
    spurious = {
        1: [1, 2],
        2: [4],
    }
    valid = remove_spurious_associations(tariffs, spurious)
    assert isinstance(valid, np.ndarray)
    assert valid[1, 1] == valid[1, 2] == valid[2, 4] == 0
    assert (tariffs[0] == valid[0]).all()
    assert (tariffs[1, 0] == valid[1, 0]).all()
    assert (tariffs[1, 3:] == valid[1, 3:]).all()
    assert (tariffs[2, 0:3] == valid[2, 0:3]).all()
    assert (tariffs[3] == valid[3]).all()

    causes = np.array(['a', 'b', 'c', 'd'])
    symps = np.array(['A', 'B', 'C', 'D', 'E'])
    spurious = {
        'b': ['B', 'C'],
        'c': ['E'],
    }
    tariffs = pd.DataFrame(tariffs, causes, symps)
    valid_df = remove_spurious_associations(tariffs, spurious, causes, symps)
    assert isinstance(valid_df, pd.DataFrame)
    assert (valid == valid_df.values).all()
    assert (valid_df.index == causes).all()
    assert (valid_df.columns == symps).all()


def test_keep_top_n_tariffs_one_row():
    top_n = 10
    start = 5
    end = 5 + top_n + 1

    tariffs = np.arange(start, end)[np.newaxis, :]
    only_top = keep_top_symptoms(tariffs, top_n)
    assert isinstance(only_top, np.ndarray)
    assert only_top[0, 0] == 0
    assert np.all(only_top[0, 1:] == np.arange(start + 1, end))
    assert np.sum(only_top > 0) == top_n
    for _ in range(10):
        np.random.shuffle(tariffs)
        only_top = keep_top_symptoms(tariffs, top_n)
        assert np.sum(only_top > 0) == top_n

    tariffs = pd.DataFrame(tariffs)
    only_top_df = keep_top_symptoms(tariffs, top_n)
    assert isinstance(only_top_df, pd.DataFrame)
    assert (only_top_df == only_top).all().all()


def test_keep_top_n_tariffs_n_larger_than_cols():
    tariffs = np.arange(10)[np.newaxis, :]
    only_top = keep_top_symptoms(tariffs, tariffs.shape[1] + 5)
    assert (only_top == tariffs).all()


def test_keep_top_n_tariffs_with_negatives():
    assert False


def test_keep_top_n_tariffs_with_ties():
    assert False


def test_keep_top_n_tariffs():
    assert False


def test_make_tariff_matrix():
    assert False


def test_score_samples():
    # 4 samples by 4 predictors
    X = np.array([[0, 0, 0, 1],
                  [1, 0, 1, 0],
                  [1, 1, 0, 0],
                  [0, 0, 0, 0]])
    # 2 causes by 4 predictors
    tariffs = np.array([[7, 5, 0, 1],
                        [1, 3, 7, 9]])
    # 4 samples by 2 causes
    expected = np.array([[1, 9],
                         [7, 8],
                         [12, 4],
                         [0, 0]])
    scored = score_samples(X, tariffs)
    assert isinstance(scored, np.ndarray)
    assert np.all(scored == expected)

    causes = np.array(['A', 'B'])
    symptoms = np.array(['a', 'b', 'c', 'd'])
    idx = np.array(['va1', 'va2', 'va3', 'va4'])
    tariffs = pd.DataFrame(tariffs, causes, symptoms)
    df = pd.DataFrame(X, idx, symptoms)

    scored = score_samples(df, tariffs)
    assert isinstance(scored, pd.DataFrame)
    assert (scored.index == idx).all()
    assert (scored.columns == causes).all()
    assert (scored == expected).all().all()


def test_generate_uniform_list_array():
    n_causes = 5
    n_symptoms = 10
    n_samples = 100
    n_samples_per_cause = 50

    X = random_ones_zeros((n_samples, n_symptoms))
    y = np.random.choice(range(n_causes), n_samples)
    tariffs = np.random.random((n_causes, n_symptoms))

    X_uniform, y_uniform = generate_uniform_list(X, y, tariffs,
                                                 n_samples=n_samples_per_cause)
    assert isinstance(X_uniform, np.ndarray)
    assert isinstance(y_uniform, np.ndarray)
    assert X_uniform.shape == (n_samples_per_cause * n_causes, n_causes)
    assert X_uniform.shape[0] == y_uniform.shape[0]
    causes, counts = np.unique(y_uniform, return_counts=True)
    assert causes.shape[0] == n_causes
    assert (counts == n_samples_per_cause).all()


def test_generate_uniform_list_dataframe():
    n_causes = 5
    n_symptoms = 10
    n_samples = 100
    n_samples_per_cause = 50

    X = random_ones_zeros((n_samples, n_symptoms))
    y = np.random.choice(range(n_causes), n_samples)
    tariffs = np.random.random((n_causes, n_symptoms))

    causes = np.array(list(map(chr, range(65, 65 + n_causes))))
    symptoms = np.array(list(map(chr, range(97, 97 + n_symptoms))))
    idx = np.array(['s{}'.format(i) for i in range(n_samples)])

    X = pd.DataFrame(X, idx, symptoms)
    y = pd.Series(y, idx)
    tariffs = pd.DataFrame(tariffs, causes, symptoms)

    X_uniform, y_uniform = generate_uniform_list(X, y, tariffs,
                                                 n_samples=n_samples_per_cause)
    assert isinstance(X_uniform, pd.DataFrame)
    assert isinstance(y_uniform, pd.Series)
    assert X_uniform.shape == (n_samples_per_cause * n_causes, n_causes)
    assert X_uniform.shape[0] == y_uniform.shape[0]
    causes, counts = np.unique(y_uniform, return_counts=True)
    assert causes.shape[0] == n_causes
    assert (counts == n_samples_per_cause).all()

    assert (X_uniform.index == y_uniform.index).all()
    assert set(X_uniform.index).issubset(X.index)
    assert X_uniform.groupby(level=0).apply(pd.DataFrame.drop_duplicates) \
                    .index.is_unique
    assert (y_uniform.groupby(level=0).nunique() == 1).all()
    assert set(y_uniform.iteritems()).issubset(y.iteritems())

    # assert (X_scored.loc[X_uniform.index] == X_uniform).all().all()


def test_calc_cutoffs():
    assert False


def test_rank_samples():
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
    expected = np.array([[6. , 6.5],
                         [4.5, 6.5],
                         [2.5, 3. ],
                         [0.5, 0.5]])

    ranked = rank_samples(X, uniform)
    assert isinstance(ranked, np.ndarray)
    assert (ranked == expected).all()

    causes = ['A', 'B']
    idx = ['va{}'.format(i) for i in range(X.shape[0])]
    df = pd.DataFrame(X, idx, causes)

    ranked = rank_samples(df, uniform)
    assert isinstance(ranked, pd.DataFrame)
    assert (ranked.columns == causes).all()
    assert (ranked.index == idx).all()
    assert (ranked == expected).all().all()


def test_mask_uncertain():
    assert False


def test_censor_predictions():
    assert False


def test_apply_restrictions():
    assert False


@pytest.mark.parametrize('n_causes', [1, 5, 10, 50])
def test_get_undetermined_proportions(n_causes):
    causes = np.arange(n_causes)
    csmf = get_undetermined_proportions(causes)
    assert np.allclose(csmf.sum(), 1)


def test_redsitribution():
    csmf = pd.Series(np.random.dirichlet(np.ones(7)),
                     index=[0, 1, 2, 3, 4, 5, np.nan])
    prop = pd.Series(np.random.dirichlet(np.ones(6)))
    csmf_new = redistribution(csmf, prop)
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
        # assert isinstance(pred, pd.Series)

    def test_no_nulls(self):
        clf = TariffClassifier(bootstraps=10)
        X = np.zeros((100, 10))
        y = np.random.choice(range(5), 100)
        pred = clf.fit(X, y).predict(X)
        # assert not pred.isnull().sum()
