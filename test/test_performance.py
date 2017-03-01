import itertools

import numpy as np
import pandas as pd
import pytest

from performance import *

seq_constructors = [list, tuple, np.array, pd.Series]
seq_pairs = list(itertools.product(seq_constructors, repeat=2))


@pytest.mark.parametrize('seq1,seq2', seq_pairs)
class TestCalcSensitivity(object):
    @pytest.mark.parametrize('actual,predicted,c', [
        ([1, 1, 2, 3, 4], [1, 1, 0, 0, 0], 1),
        (['a', 'a', 'b', 'c', 'd'], ['a', 'a', 'x', 'x', 'x'], 'a'),
    ])
    def test_all_correct(self, actual, predicted, c, seq1, seq2):
        stat = calc_sensitivity(c, seq1(actual), seq2(predicted))
        assert stat == 1

    @pytest.mark.parametrize('actual,predicted,c', [
        ([1, 1, 2, 3, 4], [0, 0, 0, 0, 0], 1),
        (['a', 'a', 'b', 'c', 'd'], ['x', 'x', 'x', 'x', 'x'], 'a'),
    ])
    def test_none_correct(self, actual, predicted, c, seq1, seq2):
        stat = calc_sensitivity(c, seq1(actual), seq2(predicted))
        assert stat == 0

    @pytest.mark.parametrize('actual,predicted,c', [
        ([1, 1, 2, 3, 4], [1, 0, 0, 0, 0], 1),
        (['a', 'a', 'b', 'c', 'd'], ['a', 'x', 'x', 'x', 'x'], 'a'),
    ])
    def test_half_correct(self, actual, predicted, c, seq1, seq2):
        stat = calc_sensitivity(c, seq1(actual), seq2(predicted))
        assert stat == 0.5
