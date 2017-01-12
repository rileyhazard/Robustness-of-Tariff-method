import inspect
from warnings import warn

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.utils import resample, safe_indexing

from performance import calc_ccc, calc_csmf_accuracy, correct_csmf_accuracy


class RandomClassifier(DummyClassifier):
    """Classifier to generate predictions uniformly at random

    Attributes:
        trained (dataframe): learned association between symptom/cause pairs
    """
    def __init__(self, random_state=None, **kwargs):
        self.strategy = 'uniform'
        self.constant = 1

        # Allow setting any random parameters to test classifier setters
        # and pass silently if given unused parameters. This behavior
        # matches the other classifiers
        args, _, _, argvalues = inspect.getargvalues(inspect.currentframe())
        argvalues.pop('self')
        argvalues.update(argvalues.pop('kwargs'))
        args.pop(0)
        for arg, val in argvalues.items():
            if arg not in args:
                warn("Setting unknown parameter: '{}'".format(arg))
            setattr(self, arg, val)

    @property
    def trained(self):
        probs = self.predict_proba(np.ones((1, len(self.classes_))))[0]
        return pd.DataFrame(probs, index=self.classes_,
                            columns=['probability'])

    def predict(self, X):
        """Perform classification on test X.

        This overrides the default behavior by of Sklearn classifiers by
        returning both individual and population level predictions. This is
        necessary because other classifiers estimate population distributions
        in a manner slightly de-coupled from individual predictions.

        Args:
            X (array-like): samples by features to test

        Returns:
            predictions (series): individual level prediction
            csmf: (series): population level predictions
        """
        pred = super(RandomClassifier, self).predict(X)
        indiv = pd.Series(pred, index=X.index)
        csmf = indiv.value_counts() / float(len(indiv))
        return indiv, csmf


def prediction_accuracy(clf, X_train, y_train, X_test, y_test, aggregate=None,
                        resample_test=True, resample_size=1):
    """Mesaure prediction accuracy of a classifier

    Args:
        clf: sklearn-like classifier object
        X_train (array-like): samples by features matrix used for training
        y_train (list-like): target values used for training
        X_test (array-like): samples by features matrix used for testing
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
    if resample_test:
        n_samples = round(resample_size * len(X_test))
        X_test, y_test = dirichlet_resample(X_test, y_test, n_samples)

    y_pred, csmf_pred = clf.fit(X_train, y_train).predict(X_test)

    y_actual = pd.Series(y_test)
    if aggregate:
        y_pred = y_pred.map(aggregate)
        y_actual = y_actual.map(aggregate)
        csmf_pred.index = csmf_pred.index.to_series().map(aggregate)
        csmf_pred = csmf_pred.groupby(level=0).sum()
    csmf_actual = y_actual.value_counts() / float(len(y_actual))

    preds = pd.concat([y_actual, y_pred], axis=1)
    preds.index.name = 'newid'
    preds.columns = ['actual', 'prediction']
    preds.reset_index(inplace=True)

    # It's possible for some classes predictions not to occur
    # These would result in missingness when aligning the csmf series
    csmf = pd.concat([csmf_actual, csmf_pred], axis=1).fillna(0)
    csmf.index.name = 'cause'
    csmf.columns = ['actual', 'prediction']
    csmf.reset_index(inplace=True)

    trained = clf.trained.reset_index()
    trained.rename(columns={trained.columns[0]: 'cause'}, inplace=True)

    ccc = pd.Series({cause: calc_ccc(cause, y_actual, y_pred)
                     for cause in y_actual.unique()})

    csmf_acc = calc_csmf_accuracy(csmf.actual, csmf.prediction)
    cccsmf_acc = correct_csmf_accuracy(csmf)
    accuracy = pd.DataFrame([{
            'mean_ccc': ccc.mean(),
            'median_ccc': ccc.median(),
            'csmf_accuracy': csmf_acc,
            'cccsmf_accuracy': cccsmf_acc,
        }], columns=['mean_ccc', 'median_ccc', 'csmf_accuracy',
                     'cccsmf_accuracy', 'converged'])

    return preds, csmf, trained, ccc, accuracy


def dirichlet_resample(X, y, n_samples=None):
    """Resample so that the predicted classes follow a dirichlet distribution

    When using a stratified split strategy for validation the cause
    distribution between the test and train splits are equal. Resampling the
    test data using a dirichlet distribution provides a cause distribution in
    the test data which is uncorrelated to the cause distribution of the
    training data. This is essential for correctly estimating accuracy at
    the population level. A classifier which knows the output distribution may
    perform very well at the population level without getting any individaul
    level predictions correct. Ensuring the distributions are uncorrelated
    guards against this bias.

    Args:
        X (array-like): samples by features matrix
        y (list-like): target values
        n_samples (int): number of samples in output. If none this defaults
            to the length of the input

    Return:
        X_new (array or dataframe): resampled data
        y_new (array or series): resampled predictions
    """
    if len(X) != len(y):
        raise ValueError("X and y must be the same length")
    if not n_samples:
        n_samples = len(X)

    classes = np.unique(y)
    n_classes = len(classes)
    distribution = np.random.dirichlet(np.ones(n_classes))
    counts = np.vectorize(int)(distribution * n_samples)
    missing = int(n_samples - np.sum(counts))
    for i in np.random.choice(range(n_classes), size=missing):
        counts[i] += 1

    X_new, y_new = [], []
    for i in range(n_classes):
        X_new.append(resample(safe_indexing(X, np.asarray(y) == classes[i]),
                              n_samples=counts[i]))
        y_new.append([classes[i]] * counts[i])

    y_new = np.concatenate(y_new)
    if isinstance(X, pd.DataFrame):
        X_new = pd.concat(X_new)
        y_new = pd.Series(y_new, index=X_new.index)
    else:
        X_new = np.vstack(X_new)

    assert len(X_new) == len(y_new) == n_samples
    return X_new, y_new


def out_of_sample_accuracy(X, y, clf, model_selector, groups=None,
                           tags=None, subset=None, aggregate=None,
                           resample_test=True, resample_size=1):
    """Mesaure out of sample accuracy of a classifier

    Args:
        X: (np.ndarray) rows are records, columns are features
        y: (np.array) predictions for each record
        clf: sklearn-like classifier object
        model_selector: (sklearn model_selection) iterator to produce
            test-train splits
            with my_split_id method added
        groups: (list-like) encoded group labels for each sample
        tags: (dict) column -> constant, added to the returned dataframe
        subset: (tuple of int) splits to perform
        aggregate: (dict): mapping of classes to new classes. Applied
            to data after predicting before calculating performance.

    Returns:
        preds (dataframe): actual and predicted values for all observations
            and for all splits
        csmfs (dataframe): actual and predicted proportions for each cause
            and for each split
        trained (dataframe): matrix of learned associations between
            cause/symptom pairs from the training data for each split
        ccc (dataframe): chance-correct concordance for each cause and for
            each split
        accuracy (dataframe): summary accuracy measures for each split
    """
    output = [[], [], [], [], []]
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

        if hasattr(model_selector, 'split_id'):
            test_groups = np.unique(safe_indexing(groups, test_index))
            split_id = model_selector.split_id(i, test_groups)
        else:
            split_id = i
        for df in results:
            df['split'] = split_id

        for i in range(len(output)):
            output[i].append(results[i])

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
        X:
        y:
        clf: sklearn-like classifier object


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
    return prediction_accuracy(clf, X, y, X, y, aggregate=aggregate,
                               resample_test=resample_test,
                               resample_size=resample_size)


def no_train(X, y, clf, aggregate=None, resample_test=True, resample_size=1):
    return prediction_accuracy(clf, None, None, X, y, aggregate=aggregate,
                               resample_test=resample_test,
                               resample_size=resample_size)
