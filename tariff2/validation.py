import logging

import numpy as np
import pandas as pd
from sklearn.utils import safe_indexing
from sklearn.utils.validation import (
    check_random_state,
    check_X_y,
    column_or_1d,
)
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import StratifiedShuffleSplit, LeavePOut

from .metrics import (
    calc_ccc,
    calc_csmf_accuracy_from_csmf,
    correct_csmf_accuracy
)


LOG = logging.getLogger('tariff2.validation')


def dirichlet_resample(arr, n_samples=None, random_state=None):
    """Resample an array drawing from a dirichlet distribution.

    Metrics which estimate the population-level accuracy of classifiers are
    sensitive to cause composition of the sample. Robust classifiers should
    perform well regardless of the cause composition. To properly assess the
    performance at the population level, the predictions should be tested
    using multiple samples with different distributions. Varying the cause
    composition accomplished by drawing samples from an uniformative dirichlet
    distribution and averaging the performance across draws.

    Args:
        arr (array-like): vector of categoricals for each sample
        n_samples (int): number of samples to draw. If None it will default
            to the length of arr
        random_state (int): seed value or np.random.RandomState instance

    Returns:
        np.array: array of new indicies

    Examples:
        >>> y_true = np.random.choice(np.arange(10), 100)
        >>> df = pd.DataFrame(np.random.randint(0, 2, size=(100, 25)))
        >>> idx = dirichlet_resample(y_true)
        >>> X = df.iloc[idx]
    """
    arr = column_or_1d(arr)
    rs = check_random_state(random_state)
    n_samples = n_samples or arr.shape[0]
    causes = np.unique(arr)

    # Draw samples from a dirichlet distribution where the alpha value for
    # each class is the same
    distribution = rs.dirichlet(np.ones(causes.shape[0]))

    # To calculate counts for each cause we multiply fractions through by the
    # desired sampled size and round down. We then add counts for the total
    # number of missing observations to achieve exactly the desired size.
    counts = (distribution * n_samples).astype(int)
    counts = counts + rs.multinomial(n_samples - counts.sum(), distribution)

    return np.concatenate([rs.choice(np.where(arr == cause)[0], size)
                           for size, cause in zip(counts, causes)])


def dirichlet_resample_X_y(X, y, n_samples=None, random_state=None):
    """Resample a matrix and an array drawing from a dirichlete distribution.

    Convinience function for jointly sampling an outcome array and a predictor
    array to a dirichlete distribution of outcomes.

    Args:
        X (matrix-like): samples by predictors array
        y (array-like sequence): vector of categoricals for each sample
        n_samples (int): number of samples to draw. If None it will default
            to the length of arr
        random_state (int): seed value or np.random.RandomState instance

    Returns:
        tuple: resampled X array, resampled y array

    See Also:
        dirichlet_resample
    """
    check_X_y(X, y, dtype=None)
    resample_index = dirichlet_resample(y, n_samples, random_state)
    return safe_indexing(X, resample_index), safe_indexing(y, resample_index)


def calc_performance(y_actual, y_pred, csmf_pred=None, split_id=''):
    """Mesaure prediction accuracy of a classifier.

    # All the outputs should be dataframes which can be concatentated and
    # saved without the index
    Args:
        clf: sklearn-like classifier object. It must implement a fit method
            with the signature ``(X, y) --> self`` and a predict method with
            a signature ``(X) --> (y, csmf)``
        X_train (dataframe): samples by features matrix used for training
        y_train (series): target values used for training
        X_actual (dataframe): samples by features matrix used for testing
        y_actual (series): target values to compare predictions against
        resample_actual (bool): resample test data to a dirichlet distribution
        resample_size (float): scalar applied to n of samples to determine
            output resample size.

    Returns:
        tuple:
            * preds (dataframe): two column dataframe with actual and predicted
                values for all observations
            * csmfs (dataframe): two column dataframe with actual and predicted
                cause-specific mortality fraction for each cause
            * trained (dataframe): matrix of learned associations between
                cause/symptom pairs from the training data
            * ccc (dataframe): chance-correct concordance for each cause in one row
            * accuracy (dataframe): summary accuracy measures in one row

    """
    preds = pd.concat([y_actual, y_pred], axis=1)
    preds.index.name = 'ID'
    preds.columns = ['actual', 'prediction']
    preds.reset_index(inplace=True)

    # Only calculate CCC for real causes. The classifier may predict causes
    # which are not in the set of true causes. This primarily occurs when
    # the classifier is run using default settings and no training or when it
    # isn't properly learning impossible causes.
    # Standardize output format (df with 1 row)
    ccc = pd.DataFrame([{cause: calc_ccc(cause, y_actual, y_pred)
                         for cause in y_actual.unique()}])

    # It's possible for some causes to not be predicted
    # These would result in missingness when aligning the csmf series
    if csmf_pred is None:
        csmf_pred = y_pred.value_counts(dropna=False, normalize=True)
    csmf_actual = y_actual.value_counts(dropna=False, normalize=True)
    csmf = pd.concat([csmf_actual, csmf_pred], axis=1).fillna(0)
    csmf.index.name = 'cause'
    csmf.columns = ['actual', 'prediction']
    csmf.reset_index(inplace=True)   # standardize output format

    csmf_acc = calc_csmf_accuracy_from_csmf(csmf.actual, csmf.prediction)
    cccsmf_acc = correct_csmf_accuracy(csmf_acc)

    # Standardize output format (df with 1 row)
    accuracy = pd.DataFrame([[
        ccc.iloc[0].mean(),
        ccc.iloc[0].median(),
        csmf_acc,
        cccsmf_acc,
    ]], columns=['mean_ccc', 'median_ccc', 'csmf_accuracy', 'cccsmf_accuracy'])

    results = (preds, csmf, ccc, accuracy)
    for result in results:
        result['split'] = split_id
    return results


def validate_splits(X, y, clf, splits, subset=None, resample_size=None,
                    random_state=None):
    """Mesaure out of sample accuracy of a classifier.

    Args:
        X (dataframe): rows are records, columns are features
        y (series): predictions for each record
        clf sklearn-like classifier object. It must implement a fit method
            with the signature ``(X, y) --> self`` and a predict method with
            a signature ``(X) --> (y, csmf)``
        n_splits (int): number of splits
        subset (tuple of ints): splits to perform
        test_size (float): proportion of data to use for the test split
        resample_size ():
        random_state: seed or random number generator object

    Returns:
        (tuple of dataframes): sames as ``calc_performance`` for every split
            in ``subset`` with results concatenated.
    """
    rs = check_random_state(random_state)
    output = [[], [], [], []]
    for i, (train_index, test_index, split_id) in enumerate(splits):
        if subset:
            start, stop = subset
            if i < start:
                continue
            if i > stop:
                break
        LOG.debug(f'Determining performance for split {split_id}')

        X_train = X.iloc[train_index]
        y_train = y.iloc[train_index]
        X_test = X.iloc[test_index]
        y_test = y.iloc[test_index]

        X_test, y_test = dirichlet_resample_X_y(X_test, y_test, resample_size,
                                                random_state=rs)

        y_pred, csmf_pred = clf.fit(X_train, y_train).predict(X_test)
        results = calc_performance(y_test, y_pred, csmf_pred, split_id)

        for i, result in enumerate(results):
            output[i].append(result)

    return list(map(pd.concat, output))


def validate_training(X, y, clf, n_splits, subset=None, resample_size=None,
                      random_state=None):
    rs = check_random_state(random_state)
    output = [[], [], [], []]
    for i in range(n_splits):
        if subset:
            start, stop = subset
            if i < start:
                continue
            if i > stop:
                break
        LOG.debug(f'Determining performance for split {i}')

        X, y = dirichlet_resample_X_y(X, y, resample_size, random_state=rs)

        y_pred, csmf_pred = clf.predict(X)
        results = calc_performance(y, y_pred, csmf_pred, i)

        for r, result in enumerate(results):
            output[r].append(result)

    return list(map(pd.concat, output))


def out_of_sample_splits(X, y, n_splits=10, test_size=.25, random_state=None):
    LOG.debug('Configure out-of-sample stratified shuffle splits')
    rs = check_random_state(random_state)
    splitter = StratifiedShuffleSplit(n_splits=n_splits, test_size=test_size,
                                      random_state=rs)
    for i, (train_index, test_index) in enumerate(splitter.split(X, y)):
        yield train_index, test_index, i


def hold_out_splits(X, y, groups, p=1, group_map=None):
    LOG.debug('Configuring hold-out splits')
    if isinstance(group_map, dict):
        group_map = group_map.get
    elif callable(group_map):
        pass
    else:
        def group_map(x):
            return x

    splitter = LeavePOut(p)
    for train_index, test_index in splitter.split(X, y, groups):
        held_out = '-'.join([group_map(g) for g in np.unique(y[test_index])])
        yield train_index, test_index, held_out


class RandomClassifier(DummyClassifier):
    """Classifier to generate predictions uniformly at random

    This subclasses sklearn.dummy.DummyClassifier and overrides the fit
    and predict method.
    """

    def __init__(self, random_state=None, **kwargs):
        self.strategy = 'uniform'
        self.constant = 1
        self.random_state = random_state
        for arg, val in kwargs.items():
            setattr(self, arg, val)

    def fit(self, X, y, sample_weight=None):
        if y is None:
            y = np.arange(10)
        return super().fit(X, y, sample_weight)

    def predict(self, X):
        """Perform classification on test X.

        This overrides the default behavior by of Sklearn classifiers by
        returning both individual and population level predictions. This is
        necessary because other classifiers estimate population distributions
        in a manner slightly de-coupled from individual predictions.

        Args:
            X (dataframe): samples by features to test

        Returns:
            tuple:
                * predictions (series): individual level prediction
                * csmf: (series): population level predictions
        """
        idx = getattr(X, 'index', np.arange(X.shape[0]))
        pred = super().predict(X)
        indiv = pd.Series(pred, index=idx)
        csmf = indiv.value_counts() / pred.shape[0]
        return indiv, csmf
