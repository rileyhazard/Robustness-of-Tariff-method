
import numpy as np
import pandas as pd

import tariff
from getters import (
    load_smartva_tariff_data,
    load_smartva_tariff_matrix,
    load_smartva_validated_data,
    get_smartva_symptom_file,
    get_cause_map,
)


RESTRICTIONS = {
    'adult': {
        'males_only': ['Prostate Cancer'],
        'females_only': [
            'Anemia',
            'Hemorrhage',
            'Hypertensive Disorder',
            'Other Pregnancy-Related Deaths',
            'Sepsis',
            'Breast Cancer',
            'Cervical Cancer',
        ],
        'min_age': [
            (15.001, [
                'Breast Cancer',
                'Cervical Cancer',
                'Colorectal Cancer',
                'Esophageal Cancer',
                'Lung Cancer',
                'Other Cancers',
                'Prostate Cancer',
                'Stomach Cancer',
            ]),
            (15, [
                'Anemia',
                'Hemorrhage',
                'Hypertensive Disorder',
                'Other Pregnancy-Related Deaths',
                'Sepsis',
            ]),
        ],
        'max_age': [
            (48.999, [
                'Anemia',
                'Hemorrhage',
                'Hypertensive Disorder',
                'Other Pregnancy-Related Deaths',
                'Sepsis',
            ]),
            (75, ['AIDS', 'AIDS with TB'])
        ],
    },
    'child': {},
    'neonate': {},
}


class SmartvaClassifier(tariff.TariffClassifier):
    def __init__(self, path, module):
        self.path = path
        self.module = module

        self.precision = 0.5
        self.top_n_symptoms = 40
        self.redistribute = True

    def fit(self, *args, **kwargs):
        tariff_data = load_smartva_tariff_data(self.path, self.module)
        self.min_cause_score = tariff_data.MIN_CAUSE_SCORE
        self.cause_pct_cutoff = tariff_data.CUTOFF_POS * 100
        self.overall_pct_cutoff = tariff_data.UNIFORM_LIST_POS * 100

        tariffs = load_smartva_tariff_matrix(self.path, self.module)
        self.causes_ = tariffs.index.values
        tariffs = self.process_smartva_tariffs(tariffs, tariff_data)

        validated = load_smartva_validated_data(self.path, self.module)
        trained = self.process_training_data(validated, tariffs, tariff_data)
        X_uniform, y_uniform, cutoff_scores, cutoff_ranks = trained

        self.tariffs_ = tariffs
        self.n_causes_ = len(self.causes_)
        self.symptoms_ = tariffs.columns.values
        self.X_uniform_ = X_uniform
        self.y_uniform_ = y_uniform
        self.cutoff_scores_ = cutoff_scores
        self.cutoff_ranks_ = cutoff_ranks

        return self

    def process_smartva_tariffs(self, tariffs, tariff_data):
        va46_to_text46 = get_cause_map(self.module, 'smartva', 'smartva_text')
        tariffs.index = tariffs.index.to_series().map(va46_to_text46)

        spurious = {va46_to_text46[k]: v
                    for k, v in tariff_data.SPURIOUS_ASSOCIATIONS.items()}

        if spurious:
            tariffs = self.remove_spurious_associations(tariffs, spurious)
        tariffs = self.keep_top_symptoms(tariffs, self.top_n_symptoms)
        tariffs = self.round_tariffs(tariffs, self.precision)
        return tariffs

    def process_training_data(self, validated, tariffs, tariff_data):
        """Transforming the training data into scored, resampled data"""
        if self.module == 'adult':
            causes = validated.gs_text46
            causes_num = validated.va46
        else:
            causes = validated.gs_text34
            causes_num = validated.va34

        # Columns must be in the same order as the tariff matrix
        validated = validated.loc[:, tariffs.columns].fillna(0)

        scored = self.score_samples(validated.values, tariffs.values)
        scored = pd.DataFrame(scored, index=validated.index,
                              columns=tariffs.index)

        # Jump through hoops to make the results match SmartVA (see below)
        # I'm looking at you reversed sorted key function.. oO
        new_index = np.repeat(*zip(*sorted(tariff_data.FREQUENCIES.items(),
                                           key=lambda x: x[0], reverse=True)))
        X_uniform = scored.loc[new_index].values
        y_uniform = causes.loc[new_index].values

        # Cutoffs are determined by working over the causes positionally
        # This requires a zero based index of
        y_num_uniform = causes_num.loc[new_index].values - 1

        cutoffs = self.calc_cutoffs(X_uniform, y_num_uniform,
                                    self.cause_pct_cutoff)
        cutoff_scores, cutoff_ranks = cutoffs

        return X_uniform, y_uniform, cutoff_scores, cutoff_ranks

    def predict(self, *args, **kwargs):
        kwargs['restrictions'] = RESTRICTIONS[self.module]
        return super(SmartvaClassifier, self).predict(*args, **kwargs)


if __name__ == '__main__':
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('module', choices=['adult', 'child', 'neonate'])
    parser.add_argument('input', help='Directory of previous Smartva output')
    parser.add_argument('output', help='Directory for output predictions')
    parser.add_argument('-smartva', help='Directory of SmartVA repo')
    args = parser.parse_args()

    if not args.smartva:
        # Assume it is next to this repo
        args.smartva = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', '..', 'smartva')

    clf = SmartvaClassifier(args.smartva, args.module).fit()

    # Columns must be in the same order as the tariff matrix and all columns
    # must be present with valid values
    df = get_smartva_symptom_file(args.input, args.module)
    X = df.loc[:, clf.tariffs_.columns].fillna(0)

    results = clf.predict(X, ages=df.real_age, sexes=df.real_gender)

    results.name = 'Prediction'
    results.index.name = 'sid'
    output_name = '{}-predictions.csv'.format(args.module)
    results.to_csv(os.path.join(args.output, output_name), header=True)
