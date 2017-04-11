from __future__ import division, print_function

import numexpr as ne
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils import check_random_state
from sklearn.utils.validation import (
    check_X_y,
    check_array,
    check_is_fitted,
    check_consistent_length,
    column_or_1d,
)

from tariff2.utils import make_mask, is_uncertain


class TariffClassifier(BaseEstimator, ClassifierMixin):
    """
    Parameters:
        precision (float): value to which tariffs are rounded
        bootstraps (int): number of bootstraps to perform to determine
            if tariffs are significant
        tariffs_ui (float): uncertainty interval for determining insignificant
            tariffs across bootstrap draws. If zero is within this interval
            the tariff will be set to zero
        top_n_symptoms (int): the number of symptom by cause to use when
            scoring samples. Symptoms with an absolute values less than the
            tariff at this position will not contribute to the tariff score
            for the given cause.
        min_cause_score (float): the minimum tariff score needed before a
            cause can be considered as a prediction
        cause_pct_cutoff (float): the percentile of the minimum cause-specific
            subset of ranks within the entire training data needed before a
            cause can be considered as a prediction. Values range from 0 to
            100.
        overall_pct_cutoff (float): the percentile of the minimum rank within
            the training needed before a cause can be considered as a
            prediction. Values range from 0 to 100.
        redistribute (bool): redistribute undetermined predictions at the
            population level
        spurious_associations (dict of lists): keys are causes
            values. Lists contain labels of predictors. Tariffs for these
            cause-symptom pairs are set to zero
        censoring (dict of lists):
        restrictions (dict): kwargs passed to apply_restrictions method
        metadata (sequence): labels for columns. The first columns from the
            test data (not the train data) are assumed to match these labels
            and are removed from the symptoms matrix. Column values which are
            currently used are: age, sex, region, rules.
        random_state (None, int, or np.RandomState): seed value

    Attributes:
        X_ (np.array): samples by symptoms binary matrix of training data
        y_ (np.array): causes for each sample in the training data
        symptoms_ (np.array): labels for symptoms
        causes_ (np.array): unique causes
        n_causes_ (int): number of unique causes
        tariffs_ (dataframe): causes by symptoms tariff matrix
        X_uniform_ (np.array): samples by causes matrix of tariff scores for
            the training data which has been resampled to a uniform cause
            distribution
        y_uniform_ (np.array): causes for each sample in X_uniform_
        cutoff_ranks_ (np.array): rank of cutoff values by cause
        cutoff_scores_ (np.array): scores at cutoff values
    """

    def __init__(self, precision=0.5, bootstraps=500, tariffs_ui=95,
                 top_n_symptoms=40, min_cause_score=0, cause_pct_cutoff=100,
                 overall_pct_cutoff=100, redistribute=True, random_state=None,
                 spurious_associations=None, metadata=None, censoring=None,
                 restrictions=None):
        self.precision = precision
        self.bootstraps = bootstraps
        self.tariffs_ui = tariffs_ui
        self.top_n_symptoms = top_n_symptoms
        self.min_cause_score = min_cause_score
        self.cause_pct_cutoff = cause_pct_cutoff
        self.overall_pct_cutoff = overall_pct_cutoff
        self.redistribute = redistribute
        self.random_state = random_state
        self.spurious_associations = spurious_associations or dict()
        self.censoring = censoring or dict()
        try:
            self.metadata = tuple(metadata)
        except TypeError:
            self.metadata = ()
        self.restrictions = restrictions

    def fit(self, X, y):
        """Train the classifier

        Args:
            X (array-like): samples by symptoms matrix of binary training data
            y (list-like): true causes for each sample

        Returns:
            self
        """
        input_is_df = isinstance(X, pd.DataFrame)
        symptoms = X.columns if input_is_df else None
        check_X_y(X, y, dtype=None)

        if self.metadata:
            if input_is_df:
                X = X.drop(list(self.metadata), axis=1)
                symptoms = symptoms[3:]
            else:
                X = X[:, len(self.metadata):]

        if symptoms is None:
            symptoms = np.arange(X.shape[1])

        self.X_ = X
        self.y_ = y
        rs = check_random_state(self.random_state)

        ui_tail = (100 - self.tariffs_ui) / 2
        ui = (ui_tail, 100 - ui_tail)
        tariffs = make_tariff_matrix(X, y, bootstraps=self.bootstraps,
                                     ui=ui, top_n=self.top_n_symptoms,
                                     precision=self.precision,
                                     spurious=self.spurious_associations,
                                     random_state=rs)
        tariffs, causes, symptoms = tariffs
        self.causes_ = causes
        self.n_causes_ = causes.shape[0]
        self.symptoms_ = symptoms
        self.tariffs_ = tariffs

        X_uniform, y_uniform = generate_uniform_list(X, y, tariffs,
                                                     random_state=rs)
        self.X_uniform_ = X_uniform
        self.y_uniform_ = y_uniform

        cause_encoding = dict(zip(causes, range(self.n_causes_)))
        y_uniform_num = pd.Series(y_uniform).map(cause_encoding).values
        cutoffs = calc_cutoffs(X_uniform, y_uniform_num, self.cause_pct_cutoff)
        cutoff_scores, cutoff_ranks = cutoffs
        self.cutoff_scores_ = cutoff_scores
        self.cutoff_ranks_ = cutoff_ranks

        return self

    def predict(self, X):
        """Predict for test samples

        If the input array is a dataframe, the predictions will be returned as
        a series and the intermediate results will be returned as dataframes.
        Otherwise the results will be returned as numpy arrays/

        Args:
            X (array-like): samples by symptoms matrix of binary testing data

        Returns:
            pred (list-like): individual level predictions
        """
        check_is_fitted(self, ['tariffs_', 'X_uniform_', 'cutoff_ranks_'])

        input_is_df = isinstance(X, pd.DataFrame)
        df_index = X.index.copy() if input_is_df else None

        if input_is_df:
            for label in self.metadata:
                setattr(self, label, X[label])
            X = X.drop(list(self.metadata), axis=1)
        else:
            for i, label in enumerate(self.metadata):
                setattr(self, label, X[:, i])
            X = X[:, len(self.metadata):]

        X = check_array(X)

        if not ((X == 1) | (X == 0)).all().all():
            raise ValueError('Some symptoms are not binary.')

        scored = score_samples(X, self.tariffs_)
        ranked = rank_samples(scored, self.X_uniform_)
        certain = mask_uncertain(scored, ranked, self.X_uniform_.shape[0],
                                 min_score=self.min_cause_score,
                                 cutoffs=self.cutoff_ranks_,
                                 min_pct=self.overall_pct_cutoff)
        uncensored = censor_predictions(X, certain, self.censoring,
                                        self.causes_, self.symptoms_)
        metadata = {label: np.asarray(getattr(self, label))
                    for label in self.metadata}
        valid = apply_restrictions(uncensored, self.causes_, metadata,
                                   self.restrictions)

        valid = pd.DataFrame(valid, df_index, self.causes_)
        pred = valid.apply(best_ranked, axis=1)

        rules = getattr(self, 'rules_', np.full(X.shape[0], np.nan))
        rules = pd.Series(rules, df_index)
        pred[rules.notnull()] = rules

        if input_is_df:
            metadata = pd.DataFrame(metadata, df_index)
            scored = pd.DataFrame(scored, df_index, self.causes_)
            ranked = pd.DataFrame(ranked, df_index, self.causes_)
            certain = pd.DataFrame(certain, df_index, self.causes_)
            uncensored = pd.DataFrame(uncensored, df_index, self.causes_)
            valid = pd.DataFrame(valid, df_index, self.causes_)
            pred = pd.Series(pred, df_index, name='prediction')

        self.metadata_ = metadata
        self.scored_ = scored
        self.ranked_ = ranked
        self.certain_ = certain
        self.valid_ = valid
        self.pred_ = pred

        return pred

    def predict_csmf(self, X):
        """Predict cause-specific mortality fractions

        Args:
            X (array-like): samples by symptoms matrix of binary testing data

        Returns:
            csmf (series): cause-specific mortality fractions
        """
        pred = self.predict(X, undetermined=np.nan)
        csmf = pred.value_counts(dropna=False) / len(pred)
        csmf = csmf.loc[list(self.causes_) + [np.nan]].fillna(0)

        if self.redistribute:
            rdp_csmf = self.get_undetermined_proportions()
            csmf = self.redistribution(csmf, rdp_csmf)

        return csmf


def calc_tariffs(X, y):
    """Calculate the tariffs for all cause-symptom pairs

    Args:
        X (matrix-like): samples by symptoms matrix of binaries
        y (list-like): causes for each sample

    Returns:
        tariffs (np.array or dataframe)
    """
    check_X_y(X, y, dtype=None)
    if not ((X == 1) | (X == 0)).all().all():
        raise ValueError('Some symptoms are not binary.')

    tariffs = pd.DataFrame(X).groupby(y).mean() \
                .apply(tariffs_from_endorsements, axis=0, raw=True)

    if isinstance(X, pd.DataFrame):
        tariffs.index.name = 'causes'
        tariffs.columns.name = 'symptoms'
    else:
        tariffs = tariffs.values
    return tariffs


def tariffs_from_endorsements(arr):
    """Calculate tariffs from a array of endorsement rates

    Args:
        arr (np.array): endorsement rates

    Returns:
        tariff values (np.array)
    """
    pct25, median, pct75 = np.percentile(arr, [25, 50, 75])
    iqr = pct75 - pct25 or 0.001
    return ne.evaluate("(arr - median) / iqr")


def boostrap_endorsements_by_causes(X, y, bootstraps=500, random_state=None):
    """


    Returns:
        (dataframe): endorsement rates multi-indexed by cause and draw
    """
    check_X_y(X, y, dtype=None)
    if not np.all((X == 1) | (X == 0)):
        raise ValueError('Some symptoms are not binary.')
    rs = check_random_state(random_state)

    def bootstrapped_endorsements(df):
        n_samples = df.shape[0] * bootstraps
        return df.iloc[rs.randint(df.shape[0], size=n_samples)] \
                 .groupby(np.repeat(np.arange(bootstraps), df.shape[0])).mean()

    endorsements = pd.DataFrame(X).groupby(y).apply(bootstrapped_endorsements)
    endorsements.index.names = ('cause', 'draw')

    return endorsements


def calc_insignificant_tariffs(X, y, bootstraps=500, ui=(2.5, 97.5),
                               random_state=None):
    """Bootstrap symptom data to determine which tariffs are signficant

    Tariff values for insignificant tariffs are set to zero. This is
    determined by bootstrapping the input data 'n' times and recalculating
    the tariff matrix for each draw. If the uncertainty interval for a
    given cause-symptom pair across the bootstraps include zero the tariff
    is insignificant. The bootstraps are only used to determine
    significance.The tariff value is from the original input data, not the
    mean across bootstrap draws.

    Args:
        X: (matrix-like) samples by symptoms matrix of binaries
        y: (list-like): causes for each sample
        n: (int) number of bootstraps
        ui: (float) uncertainty interval between 0 and 100
        random_state (None, int, np.RandomState): seed

    Returns:
        insigificance (dataframe): booleans where true indicates
            the tariff is insignificant
    """
    input_is_df = isinstance(X, pd.DataFrame)

    if len(ui) != 2:
        raise ValueError('"ui" must be a 2-tuple of floats')
    ui = sorted(ui)

    endors = boostrap_endorsements_by_causes(X, y, bootstraps, random_state)
    insig = endors.groupby(level='draw') \
                  .apply(lambda df: df.apply(tariffs_from_endorsements,
                                             raw=True)) \
                  .groupby(level='cause') \
                  .apply(lambda df: df.apply(is_uncertain, raw=True, ui=ui))

    if not input_is_df:
        insig = insig.values
    return insig


def round_tariffs(tariffs, p=0.5):
    """Round tariffs to a given precision

    Args:
        tariffs (dataframe): causes by symptoms matrix of tariffs
        p (float): precision for rounding

    Returns:
        tariffs (dataframe): rounded tariff values
    """
    arr = check_array(tariffs)
    arr = np.apply_over_axes(lambda x, a: np.round(x / p) * p, arr, 1)
    if isinstance(tariffs, pd.DataFrame):
        arr = pd.DataFrame(arr, tariffs.index, tariffs.columns)
    return arr


def remove_spurious_associations(tariffs, spurious, causes=None,
                                 symptoms=None):
    """Remove specified spurious associations from tariff matrix

    Args:
        tariffs (dataframe):causes by symptoms matrix of tariffs
        spurious (dict): keys are causes, values are lists of symptoms

    Returns:
        tariffs (dataframe): a copy of the tariff matrix with spurious
            associations set to zero
    """
    arr = check_array(tariffs, copy=True)
    if causes is None:
        causes = np.arange(tariffs.shape[0])
    if symptoms is None:
        symptoms = np.arange(tariffs.shape[1])

    mask = make_mask(spurious, symptoms, causes).T
    arr[mask] = 0

    if isinstance(tariffs, pd.DataFrame):
        arr = pd.DataFrame(arr, tariffs.index, tariffs.columns)
    return arr


def keep_top_symptoms(tariffs, top_n=40):
    """Replace tariffs below the top N with a value of zero

    Args:
        tariffs (dataframe): causes by symptoms matrix of tariffs
        top_n (int): number of values to keep

    Returns
        tariffs (dataframe): causes by symptoms tariff matrix with values
            under the top N set to zero
    """
    arr = check_array(tariffs)

    if tariffs.shape[1] > top_n:
        arr[arr < np.partition(np.abs(arr), -top_n, 1)[:, -top_n, None]] = 0

    if isinstance(tariffs, pd.DataFrame):
        arr = pd.DataFrame(arr, index=tariffs.index, columns=tariffs.columns)
    return arr


def make_tariff_matrix(X, y, bootstraps=500, ui=(2.5, 97.5), random_state=None,
                       spurious=None, top_n=40, precision=0.5):
    """Fully process raw symptom data to create a tariff matrix.

    Args:

    Returns:
        tariffs (np.array or dataframe): causes by symptoms matrix of tariffs
        causes (np.array): cause labels as ordered in the tariffs matrix
        symptoms (np.array): symptoms labels as ordered in tariff matrix.
    """
    input_is_df = isinstance(X, pd.DataFrame)
    symptoms = X.columns if input_is_df else None
    X, y = check_X_y(X, y, dtype=None)
    if symptoms is None:
        symptoms = np.arange(X.shape[1])

    causes = np.unique(y)
    tariffs = calc_tariffs(X, y)
    insig = calc_insignificant_tariffs(X, y, ui=ui, bootstraps=bootstraps,
                                       random_state=random_state)
    tariffs[insig] = 0

    if spurious:
        tariffs = remove_spurious_associations(tariffs, spurious)

    if top_n:
        tariffs = keep_top_symptoms(tariffs, top_n)

    if precision:
        tariffs = round_tariffs(tariffs, precision)

    if input_is_df:
        tariffs = pd.DataFrame(tariffs, causes, symptoms)

    return tariffs, causes, symptoms


def score_samples(X, tariffs):
    """Determine tariff score by cause from symptom data

    Args:
        X (array-like) samples by symptoms matrix of binaries
        tariffs (array-like): causes by symptoms matrix of tariffs

    Returns:
        scored (np.array): samples by tariff matrix of tariff scores
    """
    input_is_df = isinstance(X, pd.DataFrame)
    df_index = X.index if input_is_df else None
    causes = tariffs.index if isinstance(tariffs, pd.DataFrame) else None

    X = check_array(X)
    tariffs = check_array(tariffs)
    scored = X[:, :, None] * tariffs.T[None, :, :]
    summed = np.apply_along_axis(np.sum, 1, scored)

    if input_is_df:
        summed = pd.DataFrame(summed, df_index, causes)

    return summed


def generate_uniform_list(X, y, tariffs, n_samples=None, random_state=None):
    """Create an array of resampled data with even an target distribution

    Args:
        X (array-like) samples by symptoms matrix of binaries
        y (list-like) causes for each sample
        tariffs (array-like) causes by symptoms matrix of tariffs
        n_samples (int): number of samples per cause. Defaults to the number
            of the most common cause in `y`

    Returns:
        X_uniform (np.array): samples by causes matrix of tariff scores
        y_uniform (np.array): causes for each sample
    """
    input_is_df = isinstance(X, pd.DataFrame)
    df_index = X.index if input_is_df else None

    X, y = check_X_y(X, y, dtype=None)
    tariffs = check_array(tariffs)
    rs = check_random_state(random_state)
    causes, counts = np.unique(y, return_counts=True)

    scored = score_samples(X, tariffs)

    if n_samples is None:
        n_samples = np.max(counts)

    idx = np.concatenate([rs.choice(np.where(y == cause)[0], n_samples)
                          for cause in causes])
    X_uniform = scored[idx]
    y_uniform = np.repeat(causes, n_samples)

    if input_is_df:
        new_index = df_index[idx]
        X_uniform = pd.DataFrame(X_uniform, new_index, causes)
        y_uniform = pd.Series(y_uniform, new_index)

    return X_uniform, y_uniform


def calc_cutoffs(X, y, cutoff=95):
    """Determine the minimum score and rank need for each cause

    The cause-specific cutoff is determined as rank within the entire
    uniformly resampled training data of the observation which has a score
    at the qth percentile by cause. The given cause is not a valid
    prediction for test observations which are ranked below this rank. If
    the given percentile is 100

    Args:
        X (array-like): samples by causes matrix of tariff scores
        y (list-like): causes for each sample
        cutoff (float): percentile used as cutoff between 0 and 100

    Returns:
        cutoffs (np.array): cutoff for each cause
    """
    input_is_df = isinstance(X, pd.DataFrame)
    causes = X.columns if input_is_df else None

    X, y = check_X_y(X, y)

    # Mergesort is needed for backwards compatibility with SmartVA
    # See regression testing for more details. Stable sorting prevents
    # variation in the cause rankings which could lead to discrepancies
    # between predictions using the same data
    X_sorted = X.argsort(0, kind='mergesort')[::-1]

    ranks, scores = [], []
    for j in range(X.shape[1]):
        ranks_j = np.where(y[X_sorted[:, j]] == j)[0] + 1
        rank = np.percentile(ranks_j, cutoff, interpolation='higher')
        ranks.append(rank)
        scores.append(X[rank - 1, j])

    if input_is_df:
        scores = pd.Series(scores, causes)
        ranks = pd.Series(ranks, causes)
    else:
        scores = np.array(scores)
        ranks = np.array(ranks)

    return scores, ranks


def rank_samples(X_test, X_train):
    """Determine rank of test samples within training data

    Args:
        X_test (array-like): samples by causes matrix of tariff scores
        X_train (array-like): samples by causes matrix of tariff scores

    Returns:
        ranked (np.array): samples by causes matrix of ranks within the
            training data for each sample in the test data
    """
    input_is_df = isinstance(X_test, pd.DataFrame)
    df_index = X_test.index if input_is_df else None
    causes = X_test.columns if input_is_df else None

    X_test = check_array(X_test)
    X_train = check_array(X_train)

    # Number of cells * 8 bytes per float in GB
    mem_req = X_test.shape[0] * X_test.shape[1] * X_train.shape[0] * 8 / 10**9
    ram = 12   # well I have 12 GB of RAM on my computer. IDK about you.

    if mem_req > ram:
        # Samples are ranked within the entire training set, however they are
        # independent of other observations. We can split the test data as
        # much as we need to, but must leave the training data intact.
        splits = int(mem_req / ram) + 1
        ranked = np.concatenate([_rank_samples(X_sub, X_train)
                                 for X_sub in np.array_split(X_test, splits)])
    else:
        ranked = _rank_samples(X_test, X_train)

    if input_is_df:
        ranked = pd.DataFrame(ranked, df_index, causes)

    return ranked


def _rank_samples(X_test, X_train):
    """Determine rank of test samples within training data

    This is a "private" version of the function which performs to array
    manipulation but does not perform input validation or type conversion.
    It is intended to be wrapped to handle memory allocation issues.

    Args:
        X_test (np.array): samples by causes matrix of tariff scores
        X_train (np.array): samples by causes matrix of tariff scores

    Returns:
        ranked (np.array): samples by causes matrix of ranks within the
            training data for each sample in the test data
    Warning:
        This function is NOT memory efficient. It creates an array in memory
        which has dimensions (X_test.shape[0], n_causes, X_train.shape[0]).
        A single 2D array of ~30,000 samples by 46 causes, the size of
        the resampled adult uniform dataset, is about 11 MB. If the test array
        has more than about 5000 samples, this function starts dragging. It
        also might explode your computer's memory, hence the warning.

    """
    X_test_3d = X_test[:, :, None]
    X_train_3d = X_train.T[None, :, :]

    lower = np.apply_along_axis(np.sum, 2, X_test_3d < X_train_3d)
    higher = np.apply_along_axis(np.sum, 2, X_test_3d > X_train_3d)

    return (lower + (X_train.shape[0] - higher)) / 2 + 0.5


def mask_uncertain(X_scores, X_ranks, train_n=np.inf, min_score=0,
                   cutoffs=None, min_pct=100):
    """Mask ranks of observations which have too little information

    Args:
        X_scores (array-like): samples by causes matrix of tariff scores
        X_ranks (array-like): samples by causes matrix of ranks
        train_n (int): number of observations in the training data
        min_score (float): minimum tariff score need before a given cause
            can be consider a valid prediction for a sample
        cutoffs (list-like): cutoff rank for each cause
        min_pct (float): percentile of training observations

    Returns:
        X_test_ranks (np.array): copy of ranks matrix with uncertain
            values set to 0.5 more than train_n
    """
    input_is_df = isinstance(X_ranks, pd.DataFrame)
    df_index = X_ranks.index if input_is_df else None
    causes = X_ranks.columns if input_is_df else None

    X_scores = check_array(X_scores)
    valid = check_array(X_ranks, copy=True, force_all_finite=False)

    overall_cutoff = train_n * min_pct / 100
    if cutoffs is not None:
        valid[X_ranks > np.asarray(cutoffs)] = np.nan
    valid[X_scores <= np.asarray(min_score)] = np.nan
    valid[X_ranks > np.asarray(overall_cutoff)] = np.nan

    if input_is_df:
        valid = pd.DataFrame(valid, df_index, causes)

    return valid


def censor_predictions(X, X_ranks, censor, causes, symptoms):
    """Calculate a mask of which cells should be censored.

    Args:
        X (matrix-like): samples by predictors matrix of binaries
        censor (dict of lists)
        causes (list-like): sequence of outcome labels
        symptoms (list-like): sequence of predictor labels

    Returns:
        censored (np.array) 2D boolean array of samples by causes where
            True indiciates a cell should be censored.
    """
    input_is_df = isinstance(X_ranks, pd.DataFrame)
    df_index = X_ranks.index if input_is_df else None

    X = check_array(X)
    if not np.all((X == 1) | (X == 0)):
        raise ValueError('Some symptoms are not binary.')
    uncensored = check_array(X_ranks, copy=True, force_all_finite=False)
    check_consistent_length(X, X_ranks)

    mask = make_mask(censor, symptoms, causes)
    censored = (X.astype(bool)[:, :, None] & mask[None, :, :]).any(1)
    uncensored[censored] = np.nan

    if input_is_df:
        uncensored = pd.DataFrame(uncensored, df_index, causes)

    return uncensored


def apply_restrictions(X, causes, metadata=None, restrictions=None):
    """Mask restricted causes based on demographics

    Args:
        X (dataframe): samples by causes matrix of tariff ranks
        ages (list-like): continuous age value for each sample
        sexes (list-like): sex of each sample codes as 1=male, 2=female
        min_age (list): tuples of (treshold, list of causes)
        max_age (list): tuples of (threshold, list of causes)
        males_only (list): causes which only occur in males
        females_only (list): causes which only occur in females
        regional (list): causes which appear in the training data, but
            are known to not occur in the prediction data
        censored (matrix-like): mask indicating which cells should be censored

    Returns:
        X_valid (np.array): A copy of X with restricted combinations
            set to the worst possible rank
    """
    input_is_df = isinstance(X, pd.DataFrame)
    df_index = X.index if input_is_df else None

    X = check_array(X, copy=True, force_all_finite=False)
    restrictions = restrictions or dict()
    metadata = metadata or dict()

    ages = metadata.get('age_', np.full(X.shape[0], np.nan))
    sexes = metadata.get('sex_', np.zeros(X.shape[0]))
    regions = metadata.get('region_', np.full(X.shape[0], np.nan))

    check_consistent_length(X, ages, sexes, regions)
    ages = column_or_1d(ages)
    sexes = column_or_1d(sexes)
    regions = column_or_1d(regions)

    for thre, labels in restrictions.get('min_age', []):
        X[(ages < thre)[:, None] & np.in1d(causes, labels)] = np.nan

    for thre, labels in metadata.get('max_age', []):
        X[(ages > thre)[:, None] & np.in1d(causes, labels)] = np.nan

    males_only = restrictions.get('males_only', [])
    X[(sexes == 2)[:, None] & np.in1d(causes, males_only)] = np.nan

    females_only = restrictions.get('females_only', [])
    X[(sexes == 1)[:, None] & np.in1d(causes, females_only)] = np.nan

    for r, labels in restrictions.get('regions', []):
        X[(regions == r)[:, None] & np.in1d(causes, labels)] = np.nan

    if input_is_df:
        pd.DataFrame(X, df_index, causes)

    return X


def best_ranked(series):
    """Determine best ranked prediction from a series of ranks"""
    if series.notnull().any():
        return series.dropna().sort_values().first_valid_index()
    else:
        return np.nan


def get_undetermined_proportions(causes):
    """Return proportions used to redistribute the undetermined CSMF"""
    # TODO: bring in external CSMF data
    # For now just redistribute evenly
    return pd.Series(np.full(len(causes), 1 / len(causes)), index=causes)


def redistribution(csmf, proportions):
    """Redistribute the undetermined predictions at the population level
    """
    predicted = csmf.drop(np.nan)
    undetermined = proportions * csmf.loc[np.nan]
    return pd.concat([predicted, undetermined]).groupby(level=0).sum()


def redistribute_undetermined(pred, weights, iso3):
    """Redistribute the undetermined proportion at the population level.

    Args:
        pred (dataframe): dataframe of individual-level predictions
            with age and sex.
        weights (dataframe): redistribution weights with a multi-index index
            of country-age-sex and columns for each cause
        iso3 (str): country of interest. This determines which weights will
            be used

    Returns:
        csmf (series): cause-specific mortality fractions across all ages
    """
    cause = 'gs_text34'
    undetermined = 'Undetermined'

    causes = weights.columns.tolist()
    weights = weights.loc[iso3].reset_index()

    csmf = pd.get_dummies(pred[cause]).mean()

    redistributed = pred.loc[pred[cause] == undetermined, ['age', 'sex']] \
                        .merge(weights, how='left')[causes].sum()
    added = redistributed / redistributed.sum() * csmf[undetermined]

    return pd.concat([added, csmf.drop(undetermined)]).groupby(level=0).sum()

