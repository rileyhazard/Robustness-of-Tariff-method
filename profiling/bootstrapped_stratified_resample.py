from __future__ import division
from operator import mul

import numexpr as ne
import numpy as np
import pandas as pd
from sklearn.utils import resample, check_X_y


###############################################################################
"""Bootstrap symptom data to determine which tariffs are signficant

Tariff values for insignificant tariffs are set to zero. This is
determined by bootstrapping the input data 'n' times and recalculating
the tariff matrix for each draw. If the uncertainty interval for a
given cause-symptom pair across the bootstraps include zero the tariff
is insignificant. The bootstraps are only used to determine
significance.The tariff value is from the original input data, not the
mean across bootstrap draws.

Tariffs are stored as a dataframe and ndarrays cannot be used as masks
for dataframes. The returned value must be a dataframe with axes
aligned with the tariffs dataframe regardless of the input type.

Args:
    X: (array-like) samples by symptoms matrix of binaries
    y: (list-like): causes for each sample
    n: (int) number of bootstraps
    ui: (float) uncertainty interval between 0 and 100

Returns:
    insigificance (dataframe): booleans where true indicates
        the tariff is insignificant
"""
###############################################################################
def to_refactor(X, y, n=500, ui=95):
    if hasattr(X, 'columns'):
        symptoms = X.columns
    else:
        symptoms = np.arange(X.shape[1])
    X, y = check_X_y(X, y)
    causes = np.unique(y)

    def calc_tariffs(X, y):
        df = pd.DataFrame(X, copy=True)
        if not df.isin([0, 1]).all().all():
            raise ValueError("Some symptoms are not binary")
        endorsements = df.groupby(y).mean()
        endorsements.index.name = 'cause'
        return endorsements.apply(_tariffs_to_refactor)

    bootstraps = []
    for x in range(n):
        X_new, y_new = [], []
        for cause in causes:
            X_new.append(resample(X[y == cause]))
            y_new.append([cause] * np.sum(y == cause))
        X_new = np.vstack(X_new)
        y_new = np.concatenate(y_new)
        tariffs = calc_tariffs(X_new, y_new)
        bootstraps.append(tariffs.values)

    ui_tail = (100 - ui) / 2
    ui = (ui_tail, 100 - ui_tail)
    insignif = np.apply_along_axis(_is_uncertain, 2, np.dstack(bootstraps), ui)

    return pd.DataFrame(insignif, index=causes, columns=symptoms)


def slightly_better(X, y, n=500, ui=95):
    if hasattr(X, 'columns'):
        symptoms = X.columns
    else:
        symptoms = np.arange(X.shape[1])
    X, y = check_X_y(X, y)
    if not np.all((X == 1) | (X == 0)):
        raise ValueError("Not all values of X are binary")

    causes = np.unique(y)

    bootstraps = []
    for x in range(n):
        X_new, y_new = [], []
        for cause in causes:
            X_new.append(resample(X[y == cause]))
            y_new.append([cause] * np.sum(y == cause))
        X_new = np.vstack(X_new)
        y_new = np.concatenate(y_new)
        tariffs = pd.DataFrame(X_new).groupby(y_new).mean() \
                    .apply(_tariffs_numexpr)
        bootstraps.append(tariffs.values)

    ui_tail = (100 - ui) / 2
    ui = (ui_tail, 100 - ui_tail)
    insignif = np.apply_along_axis(_is_uncertain, 2, np.dstack(bootstraps), ui)

    return pd.DataFrame(insignif, index=causes, columns=symptoms)


def nested_for_loops(X, y, n=500, ui=95):
    if hasattr(X, 'columns'):
        symptoms = X.columns
    else:
        symptoms = np.arange(X.shape[1])
    X, y = check_X_y(X, y)
    if not np.all((X == 1) | (X == 0)):
        raise ValueError("Not all values of X are binary")

    causes = np.unique(y)

    bootstraps = list()
    for _ in range(n):
        X_new, y_new = list(), list()
        for cause in causes:
            this_cause = y == cause
            X_new.append(resample(X[this_cause]))
            y_new.append(np.full(np.sum(this_cause), cause,
                                 dtype=np.array(cause).dtype))
        X_new = np.vstack(X_new)
        y_new = np.concatenate(y_new)
        tariffs = pd.DataFrame(X_new).groupby(y_new).mean() \
                    .apply(_tariffs_numexpr, raw=True)

        bootstraps.append(tariffs.values)

    ui_tail = (100 - ui) / 2
    ui = (ui_tail, 100 - ui_tail)
    insignif = np.apply_along_axis(_is_uncertain, 2, np.dstack(bootstraps), ui)

    return pd.DataFrame(insignif, index=causes, columns=symptoms)


def nested_for_loops_cached(X, y, n=500, ui=95):
    if hasattr(X, 'columns'):
        symptoms = X.columns
    else:
        symptoms = np.arange(X.shape[1])
    X, y = check_X_y(X, y)
    if not np.all((X == 1) | (X == 0)):
        raise ValueError("Not all values of X are binary")

    causes, counts = np.unique(y, return_counts=True)
    y_new = np.repeat(causes, counts)
    mask = {cause: y == cause for cause in causes}

    bootstraps = list()
    for _ in range(n):
        X_new = np.vstack([resample(X.compress(mask[cause], 0))
                           for cause in causes])
        tariffs = pd.DataFrame(X_new).groupby(y_new).mean() \
                    .apply(_tariffs_numexpr, raw=True)
        bootstraps.append(tariffs.values)

    ui_tail = (100 - ui) / 2
    ui = (ui_tail, 100 - ui_tail)
    insignif = np.apply_along_axis(_is_uncertain, 2, np.dstack(bootstraps), ui)

    return pd.DataFrame(insignif, index=causes, columns=symptoms)


def for_bootstrap_groupby_apply(X, y, n=500, ui=95):
    if hasattr(X, 'columns'):
        symptoms = X.columns
    else:
        symptoms = np.arange(X.shape[1])
    X, y = check_X_y(X, y)
    if not np.all((X == 1) | (X == 0)):
        raise ValueError("Not all values of X are binary")
    causes = np.unique(y)

    by_y = pd.DataFrame(X).groupby(y)
    bootstraps = [by_y.apply(lambda df: resample(df).mean())
                      .apply(_tariffs_numexpr, raw=True).values
                  for _ in range(n)]

    ui_tail = (100 - ui) / 2
    ui = (ui_tail, 100 - ui_tail)
    insignif = np.apply_along_axis(_is_uncertain, 2, np.dstack(bootstraps), ui)

    return pd.DataFrame(insignif, index=causes, columns=symptoms)


def groupby_apply_bootstrap(X, y, n=500, ui=95):
    if hasattr(X, 'columns'):
        symptoms = X.columns
    else:
        symptoms = np.arange(X.shape[1])
    X, y = check_X_y(X, y)
    if not np.all((X == 1) | (X == 0)):
        raise ValueError("Not all values of X are binary")

    ui_tail = (100 - ui) / 2
    ui = (ui_tail, 100 - ui_tail)

    rs = np.random.RandomState()

    def resampled_bootstrapped_endorsements(df):
        return df.iloc[rs.randint(df.shape[0], size=df.shape[0] * n)] \
                 .groupby(np.repeat(np.arange(n), df.index.shape[0])).mean()

    return pd.DataFrame(X, columns=symptoms) \
             .groupby(y).apply(resampled_bootstrapped_endorsements) \
             .groupby(level=1) \
             .apply(lambda df: df.apply(_tariffs_numexpr, raw=True)) \
             .groupby(level=0) \
             .apply(lambda df: df.apply(_is_uncertain, raw=True, ui=ui))


###############################################################################
"""Calculate tariffs for a symptom predictor from endorsement rates of that
   predictor for all causes

Args:
    seq (sequence of floats): endorsement rates bewteen 0 and 1

Returns:
    seq (sequence of floats): tariff values for each cause
"""
###############################################################################
def _tariffs_to_refactor(seq):
    median = seq.median()
    pct25, pct75 = tuple(seq.quantile([.25, .75]))
    iqr = pct75 - pct25
    if iqr == 0:
        iqr = 0.001
    return seq.map(lambda x: (x - median) / iqr)


def _tariffs_series(seq):
    pct25, median, pct75 = seq.quantile([.25, .50, .75])
    iqr = pct75 - pct25
    if iqr == 0:
        iqr = 0.001
    return seq.map(lambda x: (x - median) / iqr)


def _tariffs_array(seq):
    pct25, median, pct75 = np.percentile(seq, [25, 50, 75])
    iqr = pct75 - pct25
    if iqr == 0:
        iqr = 0.001
    return pd.Series(seq).map(lambda x: (x - median) / iqr)


def _tariffs_numexpr(seq):
    pct25, median, pct75 = np.percentile(seq, [25, 50, 75])
    iqr = pct75 - pct25 or 0.001
    return ne.evaluate("(seq - median) / iqr")


###############################################################################
"""Returns True if the uncertainty interval of the array contains zero

Args:
    arr (list-like): sequence of values
    ui: (tuple of two float): upper and lower bounds of uncertainty interval,
        scaled between 0 and 100

Returns:
    (bool)
"""
###############################################################################
def _is_uncertain(arr, ui):
    lower, upper = np.percentile(arr, ui)
    return lower < 0 and upper > 0


def _is_uncertain_never_write_this(arr, ui):
    return mul(*np.percentile(arr, ui)) < 0


###############################################################################
if __name__ == '__main__':
    X = np.random.choice([0, 1], (8000, 250), p=[.92, .08])
    y = np.random.choice(40, 8000)
    groupby_apply_bootstrap(X, y, 500)
