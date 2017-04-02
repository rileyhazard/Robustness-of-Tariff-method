import math

import pandas as pd
import numpy as np

from tariff2.utils import safe_align_sequences


def calc_sensitivity(class_, actual, predicted):
    """Calculate sensitivity for a single class

    Sensitivity is also known true positive rate, recall, or probability of
    detection. It is the number of correct predictions for the given class
    over the total number of predictions for the class.

    .. math::
        sensitivity = \\frac{TP}{P} = \\frac{TP}{TP + FN}

    where TP is the number of true postives prections, P is the number of true
    positives in the sample, and FN is the number of false positives
    predictions.

    Args:
        class_: a label in the actual and predicted arrays
        actual (sequence): true individual level classification
        predicted (sequence): individual level prediction

    Returns:
        float
    """
    actual, predicted = safe_align_sequences(actual, predicted)
    true_positive = ((actual == class_) & (predicted == class_)).sum()
    n_predicted = (actual == class_).sum()
    return true_positive / n_predicted if n_predicted else np.nan


def calc_specificity(class_, actual, predicted):
    """Calculate specificity for a single class

    Specificity is also know as the true negative rate. It is the number of
    prediction which are correctly determined to not belong to the given
    class over the total number that to not belong to the class.

    .. math::
        specificity = \\frac{TN}{N} = \\frac{TN}{TN + FP}

    where TN is the number of true negatives predictions, N is the number of
    samples which are not the given class, and FP is the number of false
    positive predictions.

    Args:
        class_: a label in the actual and predicted arrays
        actual (sequence): true individual level classification
        predicted (sequence): individual level prediction

    Returns:
        float
    """
    actual, predicted = safe_align_sequences(actual, predicted)
    true_negative = ((actual != class_) & (predicted != class_)).sum()
    n_not_class = (actual != class_).sum()
    return true_negative / n_not_class if n_not_class else np.na


def calc_positive_predictive_value(class_, actual, predicted):
    """Calculate positive predictive value (PPV) for a single class

    Positive predictive value is also known as precision. It is the number of
    correct predictions for a given class over the total number of predictions
    of the class.

    .. math::
         PPV = \\frac{TP}{PP} = \\frac{TP}{TP + FP}

    where TP is the number of true positive predictions, PP is the number of
    positive predictions, and FP is the number of false positive predictions.

    Args:
        class_: a label in the actual and predicted arrays
        actual (sequence): true individual level classification
        predicted (sequence): individual level prediction

    Returns:
        float
    """
    actual, predicted = safe_align_sequences(actual, predicted)
    true_positive = ((actual == class_) & (predicted == class_)).sum()
    n_called = (predicted == class_).sum()
    return true_positive / n_called if n_called else np.nan


def calc_negative_predictive_value(class_, actual, predicted):
    """Calculate negative predictive value (NPV) for a single class

    Negative predictive value is the number of prediction correctly determined
    to not belong to the given class over the total number of predicted to
    not belong to the class.

    .. math::
         PPV = \\frac{TP}{PP} = \\frac{TP}{TP + FP}

    where TP is the number of true positive predictions, PP is the number of
    positive predictions, and FP is the number of false positive predictions.

    Args:
        class_: a label in the actual and predicted arrays
        actual (sequence): true individual level classification
        predicted (sequence): individual level prediction

    Returns:
        float
    """
    actual, predicted = safe_align_sequences(actual, predicted)
    true_negative = ((actual != class_) & (predicted != class_)).sum()
    n_not_predicted = (predicted != class_).sum()
    return true_negative / n_not_predicted if n_not_predicted else np.na


def calc_specific_accuracy(class_, actual, predicted):
    """Calculate accuracy for a single class

    Accuracy for a single class is the number of predictions correctly
    classified with regard to this class over the entire population.
    Misclassification of other labels among true negative predictions does
    not affect this statistic.

    .. math::
        accuracy = \\frac{TP + TN}{TP + FP + FN + TN}

    Args:
        class_: a label in the actual and predicted arrays
        actual (sequence): true individual level classification
        predicted (sequence): individual level prediction

    Returns:
        float
    """
    actual, predicted = safe_align_sequences(actual, predicted)
    true_positive = ((actual == class_) & (predicted == class_)).sum()
    true_negative = ((actual != class_) & (predicted != class_)).sum()
    return (true_positive + true_negative) / len(actual)


def calc_ccc(class_, actual, predicted):
    """Calculate chance-corrected concordance for a single class

    Chance corrected metrics are derived from the general equation:

    .. math::

        K_j = \\frac{P(observed)_j - P(expected)_j}{1 - P(expected)_j}

    where K\ :sub:`J` is the corrected statistic for class j, P(observed)\
    :sub:`j` is the observed probability of j, and P(expected)\ :sub:`j` is
    the expected probability of j.

    Concordance is a multiclass generalization of sensitivity which captures
    number of observation on the diagonal of the misclassification matrix over
    the whole sample. This is corrected for chance by making the naive
    assumption that the likelihood of predicting a given class purely by chance
    is uniformly distributed across class. This differs from Cohen's kappa
    which assumes the likelihood of predicting a class purely due to chance is
    a function of its true prevalences in the sample. The naive assumption
    gives estimates which are more comparable across study populations with
    different true underlying class distributions and across studies which use
    different number of classes. For class j, CCC is calculated as:

    .. math::
       CCC_j = \\frac{\\Big( \\frac{TP_j}{TP_j + FN_j}\\Big) - (\\frac{1}{N})}
               {1 - (\\frac{1}{N})}

    where TP is the true positive rate and FN is the false negative rate
    and N is the total number of observations.

    Args:
        class_: a label in the actual and predicted arrays
        actual (sequence): true individual level classification
        predicted (sequence): individual level predictions

    Returns:
        ccc (float): Chance correct concordance
    """
    sensitivity = calc_sensitivity(class_, actual, predicted)
    chance = 1 / len(np.unique(actual))
    return (sensitivity - chance) / (1 - chance)


def calc_overall_correctness(actual, predicted):
    """Calculate the proportion of correct individual-level predictions

    Args:
        actual (sequence): true individual level classification
        predicted (sequence): individual level prediction

    Return:
        float
    """
    actual, predicted = safe_align_sequences(actual, predicted)
    return (actual == predicted).sum() / len(actual)


def agg_cause_specific_metrics(agg, metric, actual, predicted, weights=None):
    """Aggregate cause specific metrics into a single estimate

    It is useful to have a single performance metric at the individual-level.
    Some metrics only produce cause-specific estimates. These estimates can be
    aggregated in different ways to produce a single overall performance
    estimate.

    Args:
        agg (function): function to aggregate across cause-specifice stimates.
            It should have the following sigature (sequence [, weights]) -->
            float where weights is an optional sequence with the same length
            as the number of actual prediction classes.
        metric (function): function to compute cause specific metrics. It
            should have the following sigature: (class, actual, predicted) -->
            float where actual and predicted are sequences and class is a
            value in the two sequences.
        actual (sequence): true individual level classification
        predicted (sequence): individual level predictions
        weights (bool or sequence): use the true distribution as weights when
            aggregating across causes

    Returns:
        float

    Example:

    >>> agg_cause_specific_metrics(np.median, calc_ccc, actual, predicted)
    >>> agg_cause_specific_metrics(np.average, calc_ccc, actual, predicted,
                                   weights=True)

    """
    if weights is True:
        csmf_true = np.unique(actual, return_counts=True)[-1] / len(actual)
        w = {'weights': csmf_true}
    elif weights:
        w = weights
    else:
        w = dict()
    return agg([metric(c, actual, predicted) for c in np.unique(actual)], **w)


def calc_median_ccc(actual, predicted):
    """Calculate median chance-corrected concordance across all classes

    Args:
        actual (sequence): true individual level classification
        predicted (sequence): individual level predictions

    Returns:
        float
    """
    return np.median([calc_ccc(class_, actual, predicted)
                      for class_ in np.unique(actual)])


def calc_mean_ccc(actual, predicted):
    """Calculate mean chance-corrected concordance across all classes

    Args:
        actual (sequence): true individual level classification
        predicted (sequence): individual level predictions

    Returns:
        float
    """
    return np.mean([calc_ccc(class_, actual, predicted)
                    for class_ in np.unique(actual)])


def calc_csmf_accuracy_from_csmf(actual, predicted):
    """Calculate Cause-Specific Mortality Fraction (CSMF) accuracy from CSMF
       estimates

    .. math::
       CSMF Accuracy = 1 - \\frac{\\sum_{j=1}^k |CSMF_j^{true}-CSMF_j^{pred}|}
                          {2 \\Big(1 - Minimum\\Big(CSMF_j^{true}\\Big)\\Big)}

    Args:
        actual (sequence): true population level CSMFs
        predicted (sequence): predicted population level CSMFs

    Returns:
        float
    """
    actual, predicted = safe_align_sequences(actual, predicted)
    if not np.allclose(actual.sum(), predicted.sum(), 1):
        raise ValueError('CSMFs must sum to 1.')
    abs_error = np.abs(actual - predicted).sum()
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
    actual, predicted = safe_align_sequences(actual, predicted)
    csmf_pred = pd.Series(predicted).value_counts(dropna=False) / len(actual)
    csmf_true = pd.Series(actual).value_counts(dropna=False) / len(actual)

    # Drop causes in the prediction which do not appear in the actual
    csmf_pred = csmf_pred.loc[csmf_true.index].fillna(0)
    return calc_csmf_accuracy_from_csmf(csmf_true, csmf_pred)


def correct_csmf_accuracy(uncorrected):
    """Correct Cause-Specific Mortality Fraction accuracy for chance

    Chance corrected metrics are derived from the general equation:

    .. math::

        K_j = \\frac{P(observed)_j - P(expected)_j}{1 - P(expected)_j}

    where K\ :sub:`j` is the corrected statistic for class j, P(observed)\
    :sub:`j` is the observed probability of j, and P(expected)\ :sub:`j` is
    the expected probability of j. It can be shown analytically and through
    simulation, that the expected CSMF accuracy tends towards 1 - e\ :sup:`-1`
    as the number of samples and classes tend towards infinity:

    .. math::

        \\lim_{N, j \\to \\infty} P(expected)_j = 1 - e^{-1}

    We use this approximation to correct CSMF accuracy for chance regardless
    of the number of samples or class:

    .. math::
        CCCSMF = \\frac{CSMF - (1 - e^{-1})}{1 - (1 - e^{-1})}
                 \\approx \\frac{CSMF - 0.632}{1 - 0.632}

    This provides a more interpretable metric in which 1.0 is perfect,
    0.0 is equivalent to chance and negative values are worst than chance.

    Args:
        uncorrected (float): Cause-Specific Mortality (CSMF) accuracy

    Returns:
        float
    """
    return (uncorrected - (1 - math.e**-1)) / (1 - (1 - math.e**-1))


def calc_cccsmf_accuracy(actual, predicted):
    """Calculate Chance-Corrected CSMF accuracy from individual level
       predictions

    Args:
        actual (sequence): true individual level classification
        predicted (sequence): individual level predictions

    Returns:
        float
    """
    return correct_csmf_accuracy(calc_csmf_accuracy(actual, predicted))


def calc_cccsmf_accuracy_from_csmf(actual, predicted):
    """Calculate Chance-Corrected Cause-Specific Mortality Fraction (CSMF)
       accuracy from CSMF estimates

    Args:
        actual (sequence): true population level CSMFs
        predicted (sequence): predicted population level CSMFs

    Returns:
        float
    """
    csmf = calc_csmf_accuracy_from_csmf(actual, predicted)
    return correct_csmf_accuracy(csmf)


def calc_individual_stats(actual, predicted):
    stats = []
    for cause in np.unique(actual):
        params = (cause, actual, predicted)
        stats.append([
            cause,
            calc_ccc(*params),
            calc_sensitivity(*params),
            calc_specificity(*params),
            calc_positive_predictive_value(*params),
            calc_negative_predictive_value(*params),
            calc_specific_accuracy(*params),
        ])
    cols = ['cause', 'ccc', 'sensitivity', 'specificity', 'ppv', 'npv',
            'accuracy']
    return pd.DataFrame(stats, columns=cols).set_index('cause')
