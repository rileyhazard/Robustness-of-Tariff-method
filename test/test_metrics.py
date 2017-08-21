import itertools

import numpy as np
import pytest

from tariff.metrics import *


def rand_uniform(rs, n_classes, n_samples):
    return rs.choice(n_classes, n_samples)


def rand_multinomial_flat(rs, n_classes, n_samples):
    counts = rs.multinomial(n_samples, np.full(n_classes, 0.1))
    arr = np.repeat(range(n_classes), counts)
    rs.shuffle(arr)
    return arr


def rand_multinomial_rand(rs, n_classes, n_samples):
    pval = rs.rand(n_classes)
    counts = rs.multinomial(n_samples, pval / pval.sum())
    arr = np.repeat(range(n_classes), counts)
    rs.shuffle(arr)
    return arr


def rand_dirichelet_flat(rs, n_classes, n_samples):
    counts = rs.multinomial(n_samples, rs.dirichlet(np.ones(n_classes)))
    arr = np.repeat(range(n_classes), counts)
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
    n_classes = 10
    n_samples = 5000
    n_bootstraps = 5000
    cccs = []
    for _ in range(n_bootstraps):
        actual = rand1(rs, n_classes, n_samples)
        predicted = rand2(rs, len(np.unique(actual)), n_samples)
        ccc = [calc_ccc(c, actual, predicted) for c in np.unique(actual)]

        # Handle unsampled classes
        if len(ccc) < n_classes:
            for i in set(range(n_classes)).difference(actual):
                ccc.insert(i, 0)
        cccs.append(ccc)
    cccs = np.array(cccs).mean(0)
    assert np.allclose(cccs, 0, atol=0.005)


def test_calc_cccsmf_random():
    rs = np.random.RandomState(2301598121)
    n_classes = 100
    n_samples = 10000
    n_bootstraps = 1000
    cccsmfs = []
    for _ in range(n_bootstraps):
        actual = rs.dirichlet(np.ones(n_classes))
        predicted = rs.choice(n_classes, n_samples)
        predicted = np.unique(predicted, return_counts=True)[-1] / n_samples

        assert np.allclose(actual.sum(), predicted.sum(), 1)
        cccsmf = calc_cccsmf_accuracy_from_csmf(actual, predicted)
        cccsmfs.append(cccsmf)
    cccsmfs = np.mean(cccsmfs)

    assert np.allclose(cccsmfs, 0, atol=0.005)
