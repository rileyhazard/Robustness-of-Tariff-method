from __future__ import division

import pandas as pd
import numpy as np


def safe_align_sequence(*seqs):
    """Align sequences accounting for pandas indicies

    Args:
        seqs (sequence)

    Returns:
        tuple of np.arrays
    """
    if any([isinstance(s, pd.core.generic.NDFrame) for s in seqs]):
        pass   # TODO: handle realigning indicies
    return (np.asarray(s) for s in seqs)


def calc_sensitivity(class_, actual, predicted):
    """Calculate sensitivity for a single class

    Sensitivity is also known true positive rate, recall, or probability of
    detection. It is the number of correct predictions for the given class
    over the total number of predictions for the class.

    Args:
        class_: a label in the actual and predicted arrays
        actual (sequence): true individual level classification
        predicted (sequence): individual level prediction

    Returns:
        float
    """
    actual, predicted = safe_align_sequence(actual, predicted)
    true_positive = ((actual == class_) & (predicted == class_)).sum()
    n_predicted = (actual == class_).sum()
    return true_positive / n_predicted if n_predicted else np.nan


def calc_specificity(class_, actual, predicted):
    """Calculate specificity for a single class

    Specificity is also know as the true negative rate. It is the number of
    prediction which are correctly determined to not belong to the given
    class over the total number that to not belong to the class.

    Args:
        class_: a label in the actual and predicted arrays
        actual (sequence): true individual level classification
        predicted (sequence): individual level prediction

    Returns:
        float
    """
    actual, predicted = safe_align_sequence(actual, predicted)
    true_negative = ((actual != class_) & (predicted != class_)).sum()
    n_not_class = (actual != class_).sum()
    return true_negative / n_not_class if n_not_class else np.na


def calc_positive_predictive_value(class_, actual, predicted):
    """Calculate positive predictive value (PPV) for a single class

    Positive predictive value is also known as precision. It is the number of
    correct predictions for a given class over the total number of predictions
    of the class.

    Args:
        class_: a label in the actual and predicted arrays
        actual (sequence): true individual level classification
        predicted (sequence): individual level prediction

    Returns:
        float
    """
    actual, predicted = safe_align_sequence(actual, predicted)
    true_positive = ((actual == class_) & (predicted == class_)).sum()
    n_called = (predicted == class_).sum()
    return true_positive / n_called if n_called else np.nan


def calc_negative_predictive_value(class_, actual, predicted):
    """Calculate negative predictive value (NPV) for a single class

    Negative predictive value is the number of prediction correctly determined
    to not belong to the given class over the total number of predicted to
    not belong to the class.

    Args:
        class_: a label in the actual and predicted arrays
        actual (sequence): true individual level classification
        predicted (sequence): individual level prediction

    Returns:
        float
    """
    actual, predicted = safe_align_sequence(actual, predicted)
    true_negative = ((actual != class_) & (predicted != class_)).sum()
    n_not_predicted = (predicted != class_).sum()
    return true_negative / n_not_predicted if n_not_predicted else np.na


def calc_prediction_accuracy(class_, actual, predicted):
    """Calculate accuracy for a single class

    Accuracy for a single class is the number of predictions correctly
    classified with regard to this class over the entire population.
    Misclassification of other labels among true negative predictions does
    not affect this statistic.

    Args:
        class_: a label in the actual and predicted arrays
        actual (sequence): true individual level classification
        predicted (sequence): individual level prediction

    Returns:
        float
    """
    actual, predicted = safe_align_sequence(actual, predicted)
    true_positive = ((actual == class_) & (predicted == class_)).sum()
    true_negative = ((actual != class_) & (predicted != class_)).sum()
    return (true_positive + true_negative) / len(actual)


def calc_ccc(class_, actual, predicted):
    """Calculate chance-corrected concordance for a single class

    Args:
        class_: a label in the actual and predicted arrays
        actual: (sequence): true individual level classification
        predicted (sequence): individual level predictions

    Returns:
        ccc (float): Chance correct concordance
    """
    sensitivity = calc_sensitivity(class_, actual, predicted)
    chance = 1 / len(np.unique(actual))
    return (sensitivity - chance) / (1 - chance)


def calc_median_ccc(actual, predicted):
    """Calculate median chance-corrected concordance across all classes

    Args:
        actual: (sequence): true individual level classification
        predicted (sequence): individual level predictions

    Returns:
        float
    """
    return np.median([calc_ccc(class_, actual, predicted)
                      for class_ in np.unique(actual)])


def calc_mean_ccc(actual, predicted):
    """Calculate mean chance-corrected concordance across all classes

    Args:
        actual: (sequence): true individual level classification
        predicted (sequence): individual level predictions

    Returns:
        float
    """
    return np.mean([calc_ccc(class_, actual, predicted)
                    for class_ in np.unique(actual)])


def calc_csmf_accuracy_from_csmf(actual, predicted):
    """Calculate Cause-Specific Mortality Fraction (CSMF) accuracy from CSMF
       estimates

    Args:
        actual (sequence or dict): true population level CSMFs
        predicted (sequence or dict): predicted population level CSMFs

    Returns:
        float
    """
    actual, predicted = safe_align_sequence(actual, predicted)
    abs_error = np.abs(predicted - actual).sum()
    return 1 - abs_error / (2 * (1 - actual.min()))


def calc_csmf_accuracy(actual, predicted):
    """Calculate Cause-Specific Mortality Fraction (CSMF) accuracy from
       individual level predictions

    Args:
        actual (sequence): true individual level classification
        predicted (sequence): individual level predictions

    Returns:
        float
    """
    actual, predicted = safe_align_sequence(actual, predicted)
    csmf_pred = pd.Series(predicted).value_counts() / float(len(predicted))
    csmf_true = pd.Series(actual).value_counts() / float(len(actual))
    return calc_csmf_accuracy_from_csmf(csmf_true, csmf_pred)


def correct_csmf_accuracy(uncorrected):
    """Correct Cause-Specific Mortality Fraction accuracy for chance

    Args:
        uncorrected (float): Cause-Specific Mortality (CSMF) accuracy

    Returns:
        float
    """
    return (uncorrected - 0.632) / (1 - 0.632)


def calc_cccsmf_accuracy(actual, predicted):
    """Calculate Chance-Corrected CSMF accuracy from individual level
       predictions

    Args:
        actual: (sequence): true individual level classification
        predicted (sequence): individual level predictions

    Returns:
        float
    """
    return correct_csmf_accuracy(calc_csmf_accuracy(actual, predicted))


def calc_cccsmf_accuracy_from_csmf(actual, predicted):
    """Calculate Chance-Corrected Cause-Specific Mortality Fraction (CSMF)
       accuracy from CSMF estimates

    Args:
        actual (sequence or dict): true population level CSMFs
        predicted (sequence or dict): predicted population level CSMFs

    Returns:
        float
    """
    csmf = calc_cccsmf_accuracy_from_csmf(actual, predicted)
    return correct_csmf_accuracy(csmf)
