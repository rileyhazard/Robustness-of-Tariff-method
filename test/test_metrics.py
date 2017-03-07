import itertools

import numpy as np
import pandas as pd
import pytest

from src.metrics import *


def rand_uniform(rs, classes=10):
    return rs.choice(range(classes), 10000)


def rand_multinomial_flat(rs, classes=10):
    counts = rs.multinomial(10000, np.full(classes, 0.1))
    arr = np.repeat(range(classes), counts)
    rs.shuffle(arr)
    return arr


def rand_multinomial_rand(rs, classes=10):
    pval = rs.rand(classes)
    counts = rs.multinomial(10000, pval / pval.sum())
    arr = np.repeat(range(classes), counts)
    rs.shuffle(arr)
    return arr


def rand_dirichelet_flat(rs, classes=10):
    counts = rs.multinomial(10000, rs.dirichlet(np.ones(classes)))
    arr = np.repeat(range(classes), counts)
    rs.shuffle(arr)
    return arr


rand_generators = [
    rand_uniform,
    rand_multinomial_flat,
    rand_multinomial_rand,
    rand_dirichelet_flat,
]
rand_gen_pairs = list(itertools.product(rand_generators, repeat=2))


@pytest.mark.parametrize('rand1,rand2', rand_gen_pairs)
def test_calc_ccc_random(rand1, rand2):
    rs = np.random.RandomState(2301598121)
    stats = []
    for _ in range(5000):
        actual = rand1(rs)
        predicted = rand2(rs, len(np.unique(actual)))
        ccc = [calc_ccc(c, actual, predicted) for c in np.unique(actual)]

        # Handle unsampled classes
        if len(ccc) < 10:
            for i in set(range(10)).difference(actual):
                ccc.insert(i, 0)
        stats.append(ccc)
    stats = np.array(stats).mean(0)
    assert np.allclose(stats, 0, atol=0.005)


def test_calc_cccsmf_random():
    rs = np.random.RandomState(2301598121)
    stats = []
    for _ in range(5000):
        actual = rs.dirichlet(np.ones(10))
        n = 10000
        predicted = pd.Series(rs.choice(range(10), n)).value_counts().values/n
        assert np.allclose(actual.sum(), predicted.sum(), 1)
        cccsmf = calc_cccsmf_accuracy_from_csmf(actual, predicted)
        stats.append(cccsmf)
    stats = np.mean(stats)
    assert np.allclose(stats, 0, atol=0.005)


