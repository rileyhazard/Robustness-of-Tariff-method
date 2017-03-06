from decimal import Decimal

import numexpr as ne
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import (check_X_y, check_array, check_is_fitted,
                                      check_consistent_length)
from sklearn.utils import resample, safe_indexing, check_random_state


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
        random_state (None, int, or np.RandomState): seed value

    Attributes:
        X_ (np.array): samples by symptoms binary matrix of training data
        y_ (np.array): causes for each sample in the training data
        symptoms_ (np.array): labels for symptoms
        causes_ (np.array): unique causes
        n_causes_ (int): number of unique causes
        cause_prior_ (np.array): cause-specific mortality fractions of
            the input data
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
                 overall_pct_cutoff=100, redistribute=True, random_state=None):
        self.precision = precision
        self.bootstraps = bootstraps
        self.tariffs_ui = tariffs_ui
        self.top_n_symptoms = top_n_symptoms
        self.min_cause_score = min_cause_score
        self.cause_pct_cutoff = cause_pct_cutoff
        self.overall_pct_cutoff = overall_pct_cutoff
        self.redistribute = redistribute
        self.random_state = random_state

    def fit(self, X, y, spurious_associations=None):
        """Train the classifier

        Args:
            X (array-like): samples by symptoms matrix of binary training data
            y (list-like): true causes for each sample
            spurious_associations (dict of lists): keys are causes
                values. Lists contain labels of predictors. Tariffs for these
                cause-symptom pairs are set to zero

        Returns:
            self
        """
        symptoms = X.columns.copy() if isinstance(X, pd.DataFrame) else None

        X, y = check_X_y(X, y)
        X = pd.DataFrame(X, columns=symptoms, copy=True)
        self.X_ = X
        self.y_ = y
        self.symptoms_ = symptoms.tolist()

        causes, counts = np.unique(y, return_counts=True)
        self.causes_ = causes
        self.n_causes_ = causes.shape[0]
        self.cause_prior_ = counts / causes.shape[0]

        rs = check_random_state(self.random_state)

        tariffs = self.calc_tariffs(X, y)
        insig = self.calc_insignificant_tariffs(X, y, ui=self.tariffs_ui,
                                                n=self.bootstraps,
                                                random_state=rs)
        tariffs[insig] = 0

        if spurious_associations:
            tariffs = self.remove_spurious_associations(tariffs,
                                                        spurious_associations)

        if self.top_n_symptoms:
            tariffs = self.keep_top_symptoms(tariffs, self.top_n_symptoms)

        if self.precision:
            tariffs = self.round_tariffs(tariffs, self.precision)

        X_uniform, y_uniform = self.generate_uniform_list(X, y, tariffs,
                                                          random_state=rs)

        cause_encoding = dict(zip(causes, range(self.n_causes_)))
        y_uniform_num = pd.Series(y_uniform).map(cause_encoding).values
        cutoffs = self.calc_cutoffs(X_uniform, y_uniform_num,
                                    self.cause_pct_cutoff)
        cutoff_scores, cutoff_ranks = cutoffs

        self.tariffs_ = tariffs
        self.X_uniform_ = X_uniform
        self.y_uniform_ = y_uniform
        self.cutoff_scores_ = cutoff_scores
        self.cutoff_ranks_ = cutoff_ranks

        return self

    def predict(self, X, undetermined='infer', rules=None, ages=None,
                sexes=None, restrictions=None, return_scores=False,
                return_ranks=False, return_certain=False,
                return_restricted=False):
        """Predict for test samples

        If the input array is a dataframe, the predictions will be returned as
        a series and the intermediate results will be returned as dataframes.
        Otherwise the results will be returned as numpy arrays/

        Args:
            X (array-like): samples by symptoms matrix of binary testing data
            undetermined: value used for undetermined predictions. If 'infer',
                undetermined observations will be coded as 'Undetermined' if
                the dtype of the y-values is string or object. Otherwise it
                will be coded as -99
            rules (list-like): rule-based predictions for each sample or
                np.nan for no prediction. These override the tariff predictions
            ages (list-like): continuous age value for each sample
            sexes (list-like): sex of each sample codes as 1=male, 2=female
            restrictions (dict): kwargs passed to apply_restrictions method
            return_scores (bool): see below
            return_ranks (bool): see below
            return_certain (bool): see below
            return_restricted (bool): see below

        Returns:
            pred (list-like): individual level predictions
            scores (array-like): samples by causes matrix of tariff scores
            ranks (array-like): samples by causes matrix of raw ranks of test
                data within the training data
            certain (array-like): samples by causes matrix of ranks after
                masking ranks below the minimum score, cause-specific cutoff
                and overall cutoff
            restricted (array-like): samples by causes matrix of final ranks
                after masking both cutoffs and demographic restriction. The
                best rank cause on this matrix is the prediction

        """
        check_is_fitted(self, ['tariffs_', 'X_uniform_', 'cutoff_ranks_'])

        input_is_df = isinstance(X, pd.DataFrame)
        df_index = X.index.copy() if input_is_df else None

        X = check_array(X)

        scored = self.score_samples(X, self.tariffs_)
        ranked = self.rank_samples(scored, self.X_uniform_)
        certain = self.mask_uncertain(scored, ranked, self.X_uniform_.shape[0],
                                      min_score=self.min_cause_score,
                                      cutoffs=self.cutoff_ranks_,
                                      min_pct=self.overall_pct_cutoff)

        certain = pd.DataFrame(certain, columns=self.causes_)
        if input_is_df:
            certain.index = df_index

        if restrictions:
            valid = self.apply_restrictions(certain, ages, sexes,
                                            **restrictions)
        else:
            valid = certain

        pred = valid.apply(self.best_ranked, axis=1)
        if np.any(np.asarray(rules)):
            check_consistent_length(pred, rules)
            rules = pd.Series(rules, index=pred.index)
            pred.loc[rules.notnull()] = rules

        # Series are evaluated as arrays for CCC calculations and Numpy
        # does not handle Nans well. These should be filled.
        if undetermined == 'infer':
            non_numerics = [np.string_, np.unicode_, np.object_]
            if self.causes_.dtype.type in non_numerics:
                fill_val = 'Undetermined'
            else:
                fill_val = -99
        else:
            fill_val = undetermined
        pred = pred.fillna(fill_val)

        if input_is_df:
            scored = pd.DataFrame(scored, index=df_index, columns=self.causes_)
            ranked = pd.DataFrame(ranked, index=df_index, columns=self.causes_)
        else:
            pred = pred.values
            certain = certain.values
            valid = valid.values

        out = [pred]
        if return_scores:
            out.append(scored)
        if return_ranks:
            out.append(ranked)
        if return_certain:
            out.append(certain)
        if return_restricted:
            out.append(valid)

        if len(out) == 1:
            return out[0]
        else:
            return tuple(out)

    def predict_csmf(self, X):
        """Predict cause-specific mortality fractions

        Args:
            X (array-like): samples by symptoms matrix of binary testing data

        Returns:
            csmf (series): cause-specific mortality fractions
        """
        pred = self.predict(X, undetermined=np.nan)
        csmf = pred.value_counts(dropna=False) / float(len(pred))
        csmf = csmf.loc[list(self.causes_) + [np.nan]].fillna(0)

        if self.redistribute:
            rdp_csmf = self.get_undetermined_proportions()
            csmf = self.redistribution(csmf, rdp_csmf)

        return csmf

    def calc_tariffs(self, X, y):
        """Calculate the tariffs for all cause-symptom pairs

        Args:
            X: (array-like) samples by symptoms matrix of binaries
            y: (list-like): causes for each sample

        Returns:
            tariffs (dataframe)
        """
        df = pd.DataFrame(X, copy=True)
        if not df.isin([0, 1]).all().all():
            raise ValueError("Some symptoms are not binary")
        endorsements = df.groupby(y).mean()
        endorsements.index.name = 'cause'

        return endorsements.apply(self.tariff_from_endorsements, axis=0)

    @staticmethod
    def tariff_from_endorsements(series):
        """Calculate tariffs from a series of endorsement rates

        Args:
            series: endorsement rates

        Returns:
            series: tariff scores
        """
        pct25, median, pct75 = np.percentile(series, [25, 50, 75])
        iqr = pct75 - pct25 or 0.001
        return ne.evaluate("(series - median) / iqr")

    def calc_insignificant_tariffs(self, X, y, n=500, ui=95,
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
            X: (array-like) samples by symptoms matrix of binaries
            y: (list-like): causes for each sample
            n: (int) number of bootstraps
            ui: (float) uncertainty interval between 0 and 100
            random_state (None, int, np.RandomState): seed

        Returns:
            insigificance (dataframe): booleans where true indicates
                the tariff is insignificant
        """
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
                        .apply(self.tariff_from_endorsements, raw=True)
            bootstraps.append(tariffs.values)

        insig = np.apply_along_axis(self._is_uncertain, 2,
                                    np.dstack(bootstraps), ui=ui)

        # ndarrays cannot be used as masks for dataframes, so the array must
        # be converted into a dataframe with axes aligned with the tariffs
        # dataframe
        return pd.DataFrame(insig, index=causes, columns=symptoms)

    @staticmethod
    def _is_uncertain(arr, ui=95):
        """Returns True if the uncertainty interval of the array contains zero

        Args:
            arr (list-like): sequence of values
            ui: (float) uncertainty interval between 0 and 100

        Returns:
            (bool)
        """
        tail = (100 - ui) / float(2)
        lower, upper = tuple(np.percentile(arr, [tail, 100 - tail]))
        return lower < 0 and upper > 0

    def round_tariffs(self, tariffs, p=0.5):
        """Round tariffs to a given precision

        Args:
            tariffs (dataframe): causes by symptoms matrix of tariffs
            p (float): precision for rounding

        Returns:
            tariffs (dataframe): rounded tariff values
        """
        return tariffs.applymap(lambda x: round(Decimal(x) / Decimal(p)) * p)

    def remove_spurious_associations(self, tariffs, spurious):
        """Remove specified spurious associations from tariff matrix

        Args:
            tariffs (dataframe):causes by symptoms matrix of tariffs
            spurious (dict): keys are causes, values are lists of symptoms

        Returns:
            tariffs (dataframe): a copy of the tariff matrix with spurious
                associations set to zero
        """
        valid = tariffs.copy()
        for cause, associations in spurious.items():
            if cause not in self.causes_:
                continue
            for symp in associations:
                if symp not in self.symptoms_:
                    continue
                valid.loc[cause, symp] = 0
        return valid

    def keep_top_symptoms(self, tariffs, top_n=40):
        """Calculate the top N tariff values for each cause

        Args:
            tariffs (dataframe): causes by symptoms matrix of tariffs
            top_n (int): number of values to keep

        Returns
            tariffs (dataframe): causes by symptoms tariff matrix with values
                under the top N set to zero
        """
        return tariffs.apply(self._keep_top_n, n=top_n, axis=1)

    @staticmethod
    def _keep_top_n(tariffs, n):
        """Calculate the top N tariff values for a single cause

        Args:
            tariffs (series): symptoms for a single cause
            n (int): number of values to keep

        Returns
            tariffs (series): symptoms for a single cause with values under the
                top N set to zero
        """
        if len(tariffs) <= n:
            return tariffs
        cutoff = tariffs.abs().sort_values(ascending=False).iloc[n - 1]
        tariffs[tariffs.abs() < cutoff] = 0
        return tariffs

    def score_samples(self, X, tariffs):
        """Determine tariff score by cause from symptom data

        Args:
            X (array-like) samples by symptoms matrix of binaries
            tariffs (array-like): causes by symptoms matrix of tariffs

        Returns:
            scored (np.array): samples by tariff matrix of tariff scores
        """
        X = check_array(X)
        tariffs = check_array(tariffs)
        scored = X[:, :, np.newaxis] * tariffs.T[np.newaxis, :, :]
        return np.apply_along_axis(np.sum, 1, scored)

    def generate_uniform_list(self, X, y, tariffs, n=None, random_state=None):
        """Create an array of resampled data with even an target distribution

        Args:
            X (array-like) samples by symptoms matrix of binaries
            y (list-like) causes for each sample
            tariffs (array-like) causes by symptoms matrix of tariffs
            n (int): number of samples per cause. Defaults to the number
                of the most common cause in `y`

        Returns:
            X_uniform (np.array): samples by causes matrix of tariff scores
            y_uniform (np.array): causes for each sample
        """
        X, y = check_X_y(X, y)
        tariffs = check_array(tariffs)
        causes, causes_counts = np.unique(y, return_counts=True)

        scored = self.score_samples(X, tariffs)
        if n is None:
            n = np.max(causes_counts)
        X_uniform, y_uniform = [], []
        for cause in causes:
            X_uniform.append(resample(scored[y == cause], n_samples=n,
                                      random_state=random_state))
            y_uniform.append(np.full(n, cause, dtype=y.dtype))
        return check_X_y(np.vstack(X_uniform), np.concatenate(y_uniform))

    def calc_cutoffs(self, X, y, q=95):
        """Determine the minimum score and rank need for each cause

        The cause-specific cutoff is determined as rank within the entire
        uniformly resampled training data of the observation which has a score
        at the qth percentile by cause. The given cause is not a valid
        prediction for test observations which are ranked below this rank. If
        the given percentile is 100

        Args:
            X (array-like): samples by causes matrix of tariff scores
            y (list-like): causes for each sample
            q (float): percentile used as cutoff between 0 and 100

        Returns:
            cutoffs (np.array): cutoff for each cause
        """
        X, y = check_X_y(X, y)

        # Mergesort is needed for backwards compatibility with SmartVA
        # See regression testing for more details
        X_sorted = X.argsort(0, kind='mergesort')[::-1]

        ranks, scores = [], []
        for j in range(X.shape[1]):
            ranks_j = np.where(y[X_sorted[:, j]] == j)[0] + 1
            rank = np.percentile(ranks_j, q, interpolation='higher')
            ranks.append(rank)
            scores.append(X[rank - 1, j])

        return scores, ranks

    def rank_samples(self, X_test, X_train):
        """Determine rank of test samples within training data

        Args:
            X_test (array-like): samples by causes matrix of tariff scores
            X_train (array-like): samples by causes matrix of tariff scores

        Returns:
            ranked (np.array): samples by causes matrix of ranks within the
                training data for each sample in the test data
        """
        X_test = check_array(X_test)
        X_train = check_array(X_train)

        lower = X_test[:, :, np.newaxis] < X_train.T[np.newaxis, :, :]
        lower = np.apply_along_axis(np.sum, 2, lower)

        higher = X_test[:, :, np.newaxis] > X_train.T[np.newaxis, :, :]
        higher = np.apply_along_axis(np.sum, 2, higher)

        return (lower + (X_train.shape[0] - higher)) / float(2) + 0.5

    def mask_uncertain(self, X_scores, X_ranks, train_n, min_score=0,
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
        X_scores = check_array(X_scores)
        valid = check_array(X_ranks, copy=True)

        overall_cutoff = float(train_n * min_pct / float(100))
        worst_rank = train_n + 0.5

        if cutoffs:
            valid[X_ranks > np.asarray(cutoffs)] = worst_rank
        valid[X_scores <= np.asarray(min_score)] = worst_rank
        valid[X_ranks > np.asarray(overall_cutoff)] = worst_rank

        return valid

    def apply_restrictions(self, X, ages, sexes, min_age=None, max_age=None,
                           males_only=None, females_only=None, regional=None,
                           ad_hoc=None):
        """Set restricted causes to the lowest rank

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
            ad_hoc (list): tuples of (cause, mask) the cause will be restricted
                where the mask is True

        Returns:
            X_valid (np.array): A copy of X with restricted combinations
                set to the worst possible rank
        """
        check_consistent_length(X, ages, sexes)
        check_array(X)
        X = X.copy()
        ages, sexes = np.asarray(ages), np.asarray(sexes)
        worst_rank = np.max(X.values)

        if min_age:
            for threshold, causes in min_age:
                causes = list(set(causes).intersection(self.causes_))
                X.loc[ages < threshold, causes] = worst_rank
        if max_age:
            for threshold, causes in max_age:
                causes = list(set(causes).intersection(self.causes_))
                X.loc[ages > threshold, causes] = worst_rank
        if males_only:
            causes = list(set(males_only).intersection(self.causes_))
            X.loc[sexes == 2, causes] = worst_rank
        if females_only:
            causes = list(set(females_only).intersection(self.causes_))
            X.loc[sexes == 1, causes] = worst_rank
        if regional:
            X.loc[:, regional] = worst_rank
        if ad_hoc:
            for cause, condition in ad_hoc:
                if cause in self.causes_:
                    X.loc[condition, cause] = worst_rank

        return X

    @staticmethod
    def best_ranked(series):
        """Determine best ranked prediction from a series of ranks"""
        if len(series.unique()) == 1:
            return np.nan
        else:
            return series.sort_values().first_valid_index()

    def get_undetermined_proportions(self):
        """Return proportions used to redistribute the undetermined CSMF"""
        # TODO: bring in external CSMF data
        # For now just redistribute evenly
        return pd.Series(np.full(self.n_causes_, 1 / float(self.n_causes_)),
                         index=self.causes_)

    def redistribution(self, csmf, proportions):
        """Redistribute the undetermined predictions at the population level
        """
        predicted = csmf.drop(np.nan)
        undetermined = proportions * csmf.loc[np.nan]
        return pd.concat([predicted, undetermined]).groupby(level=0).sum()


if __name__ == '__main__':
    import argparse
    import inspect
    import os

    from getters import (
        get_cause_map,
        get_gold_standard,
        get_smartva_symptom_file,
        get_metadata,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', choices=['phmrc', 'nhmrc'])
    parser.add_argument('module', choices=['adult', 'child', 'neonate'])
    parser.add_argument('input', help='Directory previous Smartva output')
    parser.add_argument('output', help='Directory for output predictions')
    parser.add_argument('--rules', action='store_true',
                        help='Use rule-based predictions in symptom file')
    parser.add_argument('-m', '--metadata', action='append',
                        help='Paths to metadata yaml files')
    args = parser.parse_args()

    metadata = get_metadata(args.metadata, args.module)

    df = get_smartva_symptom_file(args.input, args.module)
    gs = get_gold_standard(args.dataset, args.module)

    matched = df.index.intersection(gs.index)
    df = df.loc[matched]
    gs = gs.loc[matched]

    cause_map = metadata.get('cause_map')
    gs = gs.gs_text46.replace(cause_map)

    non_binary = ['real_age', 'real_gender', 'cause']
    X = df.drop(non_binary, axis=1).astype(int).fillna(0)
    ages = df.real_age
    sexes = df.real_gender
    if args.rules:
        va46_to_text46 = get_cause_map(args.module, 'smartva', 'smartva_text')
        ruled = df.cause.astype(int).replace(va46_to_text46).replace(cause_map)
    else:
        ruled = None

    init, _, _, _ = inspect.getargspec(TariffClassifier.__init__)
    init.remove('self')

    clf = TariffClassifier(**{k: v for k, v in metadata.items() if k in init})
    print clf
    clf.fit(X, gs, metadata.get('spurious_associations'))
    results = clf.predict(X, ages=ages, sexes=sexes, rules=ruled,
                          restrictions=metadata.get('restrictions'))

    results.name = 'Prediction'
    results.index.name = 'sid'
    output_name = '{}-predictions.csv'.format(args.module)
    results.to_csv(os.path.join(args.output, output_name), header=True)
