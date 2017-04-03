from __future__ import division, print_function

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit, LeavePGroupsOut
from sklearn.utils import resample, safe_indexing
from sklearn.utils.validation import check_X_y

from tariff2.metrics import (
    calc_ccc,
    calc_csmf_accuracy_from_csmf,
    correct_csmf_accuracy
)


def prediction_accuracy(clf, X_train, y_train, X_test, y_test, aggregate=None,
                        resample_test=True, resample_size=1):
    """Mesaure prediction accuracy of a classifier.

    Args:
        clf: sklearn-like classifier object. It must implement a fit method
            with the signature ``(X, y) --> self`` and a predict method with
            a signature ``X --> y``
        X_train (matrix-like): samples by features matrix used for training
        y_train (list-like): target values used for training
        X_test (matrix-like): samples by features matrix used for testing
        y_test (list-like): target values to compare predictions against
        aggregate (dict): mapping of classes to new classes. Applied
            to the predictions before calculating performance.
        resample_test (bool): resample test data to a dirichlet distribution
        resample_size (float): scalar applied to n of samples to determine
            output resample size.

    Returns:
        preds (dataframe): two column dataframe with actual and predicted
            values for all observations
        csmfs (dataframe): two column dataframe with actual and predicted
            proportions for each cause
        trained (dataframe): matrix of learned associations between
            cause/symptom pairs from the training data
        ccc (dataframe): chance-correct concordance for each cause in one row
        accuracy (dataframe): summary accuracy measures in one row
    """
    check_X_y(X_train, y_train, dtype=None)
    check_X_y(X_test, y_test, dtype=None)

    if resample_test:
        n_samples = round(resample_size * len(X_test))
        X_test, y_test = dirichlet_resample(X_test, y_test, n_samples)

    y_pred = clf.fit(X_train, y_train).predict(X_test)
    y_pred = pd.Series(y_pred)

    # Some classifier (like Tariff and InSilicoVA) calculate population level
    # estimates in a manner slightly decoupled from the individual
    # predictions. If this is  the case, use these estimates instead of
    # collapsing individual predictions.
    if hasattr(clf, 'csmf'):
        csmf_pred = clf.csmf
    else:
        csmf_pred = y_pred.value_counts(dropna=False) / len(y_pred)

    y_actual = pd.Series(y_test)

    if aggregate:
        if any([isinstance(x, str) for x in aggregate.keys()]):
           y_pred = y_pred.astype(np.object_)
        y_pred = y_pred.replace(aggregate)
        y_actual = y_actual.replace(aggregate)
        csmf_pred.index = csmf_pred.index.to_series().astype(np.object_).replace(aggregate)
        #import pdb; pdb.set_trace()
        if not csmf_pred.index.is_unique:
            csmf_pred = csmf_pred.groupby(level=0).sum()

    csmf_actual = y_actual.value_counts() / len(y_actual)

    # Undetermined individual predictions are coded as nan and are dropped
    # by value_count. Rescale the total predicted csmf to be 1.
    csmf_pred = csmf_pred / csmf_pred.sum()
    assert np.allclose(csmf_pred.sum(), csmf_actual.sum(), 1)

    preds = pd.concat([y_actual, y_pred], axis=1)
    preds.index.name = 'sid'
    preds.columns = ['actual', 'prediction']

    # It's possible for classifier to not predict classes in the training data.
    # Non-sklearn classifiers (like Tariff) can also predict classes other
    # than those in the train set (e.g. missing). Preserve these additional
    # classes to return.
    csmf = pd.concat([csmf_actual, csmf_pred], axis=1).fillna(0)
    csmf.index.name = 'cause'
    csmf.columns = ['actual', 'prediction']

    ccc = pd.Series({cause: calc_ccc(cause, y_actual, y_pred)
                     for cause in y_actual.unique()})

    # Use all and only the classes from the training data to predict csmf
    causes = csmf_actual.index
    csmf_acc = calc_csmf_accuracy_from_csmf(csmf['actual'],
                                            csmf['prediction'])
    cccsmf_acc = correct_csmf_accuracy(csmf_acc)

    accuracy = pd.DataFrame([[
        ccc.mean(),
        ccc.median(),
        csmf_acc,
        cccsmf_acc,
    ]], columns=['mean_ccc', 'median_ccc', 'csmf_accuracy', 'cccsmf_accuracy'])

    preds.reset_index(inplace=True)
    ccc = ccc.reset_index()
    ccc.columns = ['cause', 'ccc']
    csmf.reset_index(inplace=True)
    return preds, csmf, ccc, accuracy


def dirichlet_resample(X, y, n_samples=None):
    """Resample so that the predicted classes follow a dirichlet distribution

    When using a stratified split strategy for validation the cause
    distribution between the test and train splits are similiar. Resampling the
    test data using a dirichlet distribution provides a cause distribution in
    the test data which is uncorrelated to the cause distribution of the
    training data. This is essential for correctly estimating accuracy at
    the population level across a variety of population. A classifier which
    knows the output distribution may perform well by only predicting the most
    common causes regardless of the predictors. This classifier would easily
    do better than chance. Alternatively, a classifier may a very high
    sensitivity for only one cause and guess at random for all other causes.
    If only tested in a population with a high prevalence of this cause, the
    classifier may appear to be very good. Neither of these provide robust
    classifier which can be widely used. Resampling the test split provides a
    better estimate of out of sample validity. The dirichlet distribution is
    conjugate prior of the multinomial distribution and always sums to one, so
    it is suitable for resampling categorical data.

    Args:
        X (matrix-like): samples by features matrix
        y (list-like): target values
        n_samples (int): number of samples in output. If none this defaults
            to the length of the input.

    Return:
        X_new (array or dataframe): resampled data
        y_new (array or series): resampled predictions
    """
    # Preserve labels from dataframes, but coerce everything else to np.array
    if isinstance(X, pd.DataFrame):
        check_X_y(X, y, dtype=None)
    else:
        X, y = check_X_y(X, y, dtype=None)

    if not n_samples:
        n_samples = len(X)

    classes = np.unique(y)

    # Draw samples from a dirichlet distribution where the alpha value for
    # each class is the same
    distribution = np.random.dirichlet(np.ones(len(classes)))

    # To calculate counts for each cause we multiply fractions through by the
    # desired sampled size and round down. We then add counts for the total
    # number of missing observations to achieve exactly the desired size.
    counts = np.vectorize(int)(distribution * n_samples)
    counts = counts + np.random.multinomial(n_samples - counts.sum(),
                                            distribution)

    X_new = [resample(safe_indexing(X, np.where(y == class_)), n_samples=cnt)
             for cnt, class_ in zip(counts, classes)]
    y_new = np.repeat(classes, counts)

    if isinstance(X, pd.DataFrame):
        X_new = pd.concat(X_new)
        y_new = pd.Series(y_new, index=X_new.index)
    else:
        X_new = np.vstack(X_new)

    return X_new, y_new


def out_of_sample_accuracy(X, y, clf, model_selector, groups=None,
                           tags=None, subset=None, aggregate=None,
                           resample_test=True, resample_size=1):
    """Mesaure out of sample accuracy of a classifier

    Args:
        X (matrix-like): samples by features matrix
        y (list-like): target values
        clf: sklearn-like classifier object
        model_selector (sklearn model_selection): iterator to produce
            test-train splits with split_id method added
        groups (list-like): encoded group labels for each sample
        tags (dict): column -> constant, identifies added to the returned
            dataframes
        subset (tuple of int): splits to perform
        aggregate (dict): mapping of classes to new classes. Applied
            to the predictions before calculating performance.
        resample_test (bool): resample test data to a dirichlet distribution
        resample_size (float): scalar applied to n of samples to determine
            output resample size.

    Returns:
        (tuple of dataframes): results ``prediction_accuracy`` concatentated
            across splits

    See Also:
        prediction_accuracy
    """
    check_X_y(X, y, dtype=None)

    output = [[], [], [], []]
    splits = model_selector.split(X, y, groups)
    for i, (train_index, test_index) in enumerate(splits):
        if subset:
            start, stop = subset
            if i < start:
                continue
            if i > stop:
                break

        # Casting as pandas objects allows this function to accept both
        # pandas an numpy inputs. It is advantageous to retain index/column
        # labels if they exist, becaues the classifiers read and store labels
        X_train = pd.DataFrame(X).iloc[train_index]
        X_test = pd.DataFrame(X).iloc[test_index]
        y_train = pd.Series(y).iloc[train_index]
        y_train.index = X_train.index
        y_test = pd.Series(y).iloc[test_index]
        y_test.index = X_test.index

        results = prediction_accuracy(clf, X_train, y_train, X_test, y_test,
                                      aggregate=aggregate,
                                      resample_test=resample_test,
                                      resample_size=resample_size)
        assert len(results) == len(output)

        try:
            test_groups = np.unique(safe_indexing(groups, test_index))
            split_id = model_selector.split_id(i, test_groups)
        except (AttributeError, TypeError):
            split_id = i

        for df in results:
            df['split'] = split_id

        for i, out in enumerate(output):
            out.append(results[i])

    for i in range(len(output)):
        output[i] = pd.concat(output[i])

    if tags:
        for i, df in enumerate(output):
            cols = df.drop('split', axis=1).columns.tolist()
            cols = tags.keys() + ['split'] + cols
            for col, tag in tags.items():
                df[col] = tag
            output[i] = df.loc[:, cols]

    return tuple(output)


def in_sample_accuracy(X, y, clf, aggregate=None, resample_test=True,
                       resample_size=1):
    """Mesaure in-sample accuracy of a classifier

    Args:
        X (matrix-like): samples by features matrix
        y (list-like): target values
        clf: sklearn-like classifier object
        aggregate (dict): mapping of classes to new classes. Applied
            to the predictions before calculating performance.
        resample_test (bool): resample test data to a dirichlet distribution
        resample_size (float): scalar applied to n of samples to determine
            output resample size.

    Returns:
        (tuple of dataframes): see ``prediction_accuracy``

    See Also:
        prediction_accuracy
    """
    return prediction_accuracy(clf, X, y, X, y, aggregate=aggregate,
                               resample_test=resample_test,
                               resample_size=resample_size)


def no_train(X, y, clf, aggregate=None, resample_test=True, resample_size=1):
    """Mesaure accuracy of a classifier of untrained classifier.

    This is only relevant for algorithms like SmartVA and InSilicoVA which
    ship with default training data.

    Args:
        X (matrix-like): samples by features matrix
        y (list-like): target values
        clf: sklearn-like classifier object
        aggregate (dict): mapping of classes to new classes. Applied
            to the predictions before calculating performance.
        resample_test (bool): resample test data to a dirichlet distribution
        resample_size (float): scalar applied to n of samples to determine
            output resample size.

    Returns:
        (tuple of dataframes): see ``prediction_accuracy``

    See Also:
        prediction_accuracy
    """
    return prediction_accuracy(clf, None, None, X, y, aggregate=aggregate,
                               resample_test=resample_test,
                               resample_size=resample_size)


def config_model_selector(model_selector, **kwargs):
    """Return an sklearn model selector object to create test-train splits

    Args:
        model_selector (str): 'sss' for StratifiedShuffleSplit or 'holdout'
            for LeavePGroupsOut
        **kwargs: parameters to pass to the model selector constructor

    Returns:
        model_selector: Sklearn object to compute test-train splits
    """
    if model_selector == 'sss':
        return config_sss_model_selector(**kwargs)
    elif model_selector == 'holdout':
        return config_holdout_model_selector(**kwargs)
    else:
        raise ValueError("Unknown model selector '{}'".format(model_selector))


def config_sss_model_selector(**kwargs):
    """Configure the StratifiedShuffleSplit model selector

    Args:
        n_splits (int): number of splits to perform [default=2]
        test_size(float): proportion of data to use in test split [default=.25]
        random_state: seed for random number generator

    Returns
        model_selectors
    """
    n_splits = kwargs.get('n_splits', 2)
    test_size = kwargs.get('test_size', .25)
    random_state = kwargs.get('random_state', np.random.RandomState(8675309))
    selector = StratifiedShuffleSplit(n_splits=n_splits, test_size=test_size,
                                      random_state=random_state)
    return selector


def config_holdout_model_selector(**kwargs):
    """Configure the LeavePGroupsOut model selector

    This adds a method to calculate the split_id from the test groups.

    Args:
        n_groups (int): number of groups in the test split [default=1]

    Returns:
        model_selector
    """
    n_groups = kwargs.get('n_groups', 1)
    selector = LeavePGroupsOut(n_groups=n_groups)

    def split_id(i, test_groups):
        return 'test:{}'.format('+'.join(map(str, np.unique(test_groups))))
    selector.split_id = split_id

    return selector
