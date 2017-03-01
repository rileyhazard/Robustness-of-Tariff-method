import math
import os

import numpy as np
import pandas as pd
import pytest
import sklearn

from code.analyze import *
from code.classifiers import random_allocation
from code.tariff import get_tariff_cause_aggregation


class TestResample(object):
    def test_baseline(self):
        x = np.zeros((5,5))
        y = np.array([1,1,1,2,2])
        d = pd.Series([.5,.5], index=[1,2])
        x_new, y_new = resample(x, y, 5, d)

    def test_fail_different_lengths(self):
        x = np.zeros((3,3))
        y = np.arange(5)
        d = pd.Series([.5,.5], index=[1,2])
        try:
            x_new, y_new = resample(x, y, 5, d)
        except AssertionError:
            x_new, y_new = ('null', 'null')
        assert x_new == y_new == 'null'

    def test_fail_non_unique_distribution(self):
        x = np.zeros((5,5))
        y = np.array([1,1,1,2,2])
        d = pd.Series([.5,.5], index=[1,1])
        try:
            x_new, y_new = resample(x, y, 5, d)
        except AssertionError:
            x_new, y_new = ('null', 'null')
        assert x_new == y_new == 'null'

    def test_fail_distribution_less_than_one(self):
        x = np.zeros((5,5))
        y = np.array([1,1,1,2,2])
        d = pd.Series([.2,.5], index=[1,1])
        try:
            x_new, y_new = resample(x, y, 5, d)
        except AssertionError:
            x_new, y_new = ('null', 'null')
        assert x_new == y_new == 'null'

    def test_fail_distribution_more_than_one(self):
        x = np.zeros((5,5))
        y = np.array([1,1,1,2,2])
        d = pd.Series([.7,.5], index=[1,1])
        try:
            x_new, y_new = resample(x, y, 5, d)
        except AssertionError:
            x_new, y_new = ('null', 'null')
        assert x_new == y_new == 'null'

    @pytest.mark.parametrize('i', [
            range(3),
            range(3,6),
            ['a', 'b', 'c'],
            ['d', 'e', 'f'],
        ])
    def test_new_prediction_in_distribution(self, i):
        x = np.zeros((5,5))
        y = np.random.choice(i, 5)
        d = pd.Series([.3, .3, .4], index=i)
        x_new, y_new = resample(x, y, 5, d)
        y_new_values = np.unique(y_new).tolist()
        assert not [n for n in y_new_values if n not in i]

    @pytest.mark.parametrize("n", [0,1,5,10,100])
    def test_output_new_n(self, n):
        x = np.zeros((5,5))
        y = np.array([1,1,1,2,2])
        d = pd.Series([.5,.5], index=[1,2])
        x_new, y_new = resample(x, y, n, d)
        assert len(x_new) == len(y_new) == n

    @pytest.mark.parametrize('distribution', [
            [.2, .3, .5],
            [.1, .1, .8],
            [.6, .3, .1],
            [.4, .2, .4],
            [1/3., 1/3., 1/3.],
            [1/4., 1/4., 1/2.],
            [.03, .17, .8]
        ])
    def test_new_y_distribution(self, distribution):
        x = np.zeros((3, 5))
        y = np.arange(3)
        d = pd.Series(distribution, index=['a', 'b', 'c'])
        n = 10
        iterations = 5000
        results = []
        for i in range(iterations):
            x_new, y_new = resample(x, y, n, d)
            d_new = pd.Series(y_new).value_counts()
            results.append(d_new)
        mean_d_new = pd.concat(results, axis=1).sum(1)/float(n * iterations)
        assert np.allclose(distribution, mean_d_new, atol=0.01)


class TestCalcSpecificCCC(object):
    def test_perfect_prediction(self):
        """4 of 4 correct"""
        i = ['a', 'b', 'c', 'd']
        a = pd.Series([1,2,1,2], index=i)
        p = pd.Series([1,2,1,2], index=i)
        ccc = calc_ccc(1, a, p)
        assert ccc == 1

    def test_at_chance(self):
        """2 possibilities and 50% (2 of 4 )correct"""
        i = ['a', 'b', 'c', 'd']
        a = pd.Series([1,2,1,2], index=i)
        p = pd.Series([1,1,2,2], index=i)
        ccc = calc_ccc(1, a, p)
        assert ccc == 0

    def test_all_wrong(self):
        """0 of 4 correct"""
        i = ['a', 'b', 'c', 'd']
        a = pd.Series([1,2,1,2], index=i)
        p = pd.Series([2,1,2,1], index=i)
        ccc = calc_ccc(1, a, p)
        assert ccc == -1

    def test_no_matching_indicies(self):
        a = pd.Series([1,2,1,2], index=['a', 'b', 'c', 'd'])
        p = pd.Series([2,1,2,1], index=['e', 'f', 'g', 'h'])
        try:
            ccc = calc_ccc(1, a, p)
        except AssertionError:
            ccc = 'null'
        assert ccc is 'null'

    def test_one_mismatched_indicies(self):
        a = pd.Series([1,2,1,2], index=['a', 'b', 'c', 'd'])
        p = pd.Series([2,1,2,1], index=['a', 'b', 'c', 'ZZZ'])
        try:
            ccc = calc_ccc(1, a, p)
        except AssertionError:
            ccc = 'null'
        assert ccc is 'null'

    def test_missing_actual_none(self):
        i = ['a', 'b', 'c', 'd']
        a = pd.Series([1,2,1,None], index=i)
        p = pd.Series([1,2,2,2], index=i)
        try:
            ccc = calc_ccc(1, a, p)
        except AssertionError:
            ccc = 'null'
        assert ccc is 'null'

    def test_missing_actual_nan(self):
        i = ['a', 'b', 'c', 'd']
        a = pd.Series([1,2,1,np.nan], index=i)
        p = pd.Series([1,2,2,2], index=i)
        try:
            ccc = calc_ccc(1, a, p)
        except AssertionError:
            ccc = 'null'
        assert ccc is 'null'

    def test_missing_prediction_none(self):
        i = ['a', 'b', 'c', 'd']
        a = pd.Series([1,2,1,2], index=i)
        p = pd.Series([1,2,2,None], index=i)
        try:
            ccc = calc_ccc(1, a, p)
        except AssertionError:
            ccc = 'null'
        assert ccc is 'null'

    def test_missing_prediction_nan(self):
        i = ['a', 'b', 'c', 'd']
        a = pd.Series([1,2,1,2], index=i)
        p = pd.Series([1,2,2,np.nan], index=i)
        try:
            ccc = calc_ccc(1, a, p)
        except AssertionError:
            ccc = 'null'
        assert ccc is 'null'

class TestCCAccuracy(object):
    def test_perfect_prediction(self):
        """All correct"""
        i = ['a', 'b', 'c', 'd']
        a = pd.Series([.5,.2,.2,.1], index=i)
        p = pd.Series([.5,.2,.2,.1], index=i)
        acc, cc_acc = calc_cc_accuracy(a, p)
        assert acc, cc_acc == (1, 1)


class TestOutOfSampleAccuracy(object):
    def test_selector_StratifiedShuffleSplit(self):
        x = np.zeros((100,5))
        y = np.array(range(5) * 20)
        g = np.array([math.floor(i/float(20)) for i in range(100)])
        ms = selector_StratifiedShuffleSplit()
        fit = random_allocation
        out_of_sample_accuracy(x,y,g,ms,fit)


    def test_selector_StratifiedShuffleSplit_splits(self):
        x = np.zeros((100,5))
        y = np.array(range(5) * 20)
        g = np.array([math.floor(i/float(20)) for i in range(100)])
        n = 5
        ms = selector_StratifiedShuffleSplit(n)
        fit = random_allocation
        results = out_of_sample_accuracy(x,y,g,ms,fit)
        summary, summ_by_pred, prediction, distribution, association = results
        assert len(summary) == n


    def test_selector_LeavePGroupsOut(self):
        x = np.zeros((100,5))
        y = np.array(range(5) * 20)
        g = np.array([math.floor(i/float(20)) for i in range(100)])
        ms = selector_LeavePGroupsOut()
        fit = random_allocation
        out_of_sample_accuracy(x,y,g,ms,fit)


    def test_selector_LeavePGroupsOut_splits(self):
        x = np.zeros((100,5))
        y = np.array(range(5) * 20)
        g = np.array([math.floor(i/float(20)) for i in range(100)])
        ms = selector_LeavePGroupsOut()
        fit = random_allocation
        results = out_of_sample_accuracy(x,y,g,ms,fit)
        summary, summ_by_pred, prediction, distribution, association = results
        assert len(summary) == len(np.unique(g))
