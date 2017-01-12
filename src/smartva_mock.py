import os
import sys

import numpy as np
import pandas as pd

from tariff import TariffClassifier


RESTRICTIONS = {
    'adult': {
        'males_only': [39],
        'females_only': [3, 20, 22, 36, 42, 6, 7],
        'min_age': [
            (15.001, [3, 20, 22, 36, 42]),
            (15, [6, 7, 9, 17, 27, 30, 39, 43]),
        ],
        'max_age': [
            (48.999, [3, 20, 22, 36, 42]),
            (75, [1, 2])
        ],
        'ad_hoc': [
            ()
        ]
    }
}


def load_smartva_data(path, module):
    sys.path.insert(0, path)
    from smartva.data import adult_tariff_data
    from smartva.data import child_tariff_data
    from smartva.data import neonate_tariff_data
    sys.path.remove(path)
    tariff_data = {
        'adult': adult_tariff_data,
        'child': child_tariff_data,
        'neonate': neonate_tariff_data
    }
    return tariff_data[module]


def load_smartva_tariff_matrix(path, module):
    matrix_path = os.path.join(path, 'smartva', 'data',
                               'tariffs-{}.csv'.format(module))
    df = pd.read_csv(matrix_path)
    df['cause'] = df.xs_name.str.lstrip('cause').astype(int)
    df = df.drop('xs_name', axis=1).set_index('cause')
    return df


def load_smartva_validated_data(path, module):
    validated_path = os.path.join(path, 'smartva', 'data',
                                  'validated-{}.csv'.format(module))
    return pd.read_csv(validated_path, index_col=0)


def process_smartva_tariffs(tariffs, precision=0.5, top_n=40, spurious=None):
    clf = TariffClassifier()
    if spurious:
        tariffs = clf.remove_spurious_associations(tariffs, spurious)
    tariffs = clf.keep_top_symptoms(tariffs, top_n)
    tariffs = clf.round_tariffs(tariffs, precision)
    return tariffs


def process_training_data(validated, tariffs, tariff_data):
    """Transforming the validated training data into scored, resampled data"""
    causes = validated.va46
    validated = validated.loc[:, tariffs.columns].fillna(0)

    clf = TariffClassifier()
    scored = pd.DataFrame(clf.score_samples(validated.values, tariffs.values),
                          index=validated.index, columns=tariffs.index)

    # Jump through hoops to make the results match SmartVA (see below)
    # I'm looking at you reversed sorted key function.. oO
    new_index = np.repeat(*zip(*sorted(tariff_data.FREQUENCIES.items(),
                                       key=lambda x: x[0], reverse=True)))
    X_uniform = scored.loc[new_index].values
    y_uniform = causes.loc[new_index].values - 1  # to match Python indicies

    cutoff_pos = tariff_data.CUTOFF_POS * 100
    cutoff_scores, cutoff_ranks = clf.calc_cutoffs(X_uniform, y_uniform,
                                                   cutoff_pos)
    return X_uniform, y_uniform, cutoff_scores, cutoff_ranks


def train_smartva_classifier(path, module):
    data = load_smartva_data(path, module)
    tariffs = load_smartva_tariff_matrix(path, module)
    validated = load_smartva_validated_data(path, module)

    tariffs = process_smartva_tariffs(tariffs,
                                      spurious=data.SPURIOUS_ASSOCIATIONS)

    trained = process_training_data(validated, tariffs, data)
    X_uniform, y_uniform, cutoff_scores, cutoff_ranks = trained

    clf = TariffClassifier(min_cause_score=data.MIN_CAUSE_SCORE,
                           cause_pct_cutoff=data.CUTOFF_POS * 100,
                           overall_pct_cutoff=data.UNIFORM_LIST_POS * 100)

    # Instead of calling the classifer's `fit` method, just load the
    # precomputed data onto the object
    clf.tariffs_ = tariffs
    clf.causes_ = tariffs.index.values
    clf.n_causes_ = len(clf.causes_)
    clf.symptoms_ = tariffs.columns.values
    clf.X_uniform_ = X_uniform
    clf.y_uniform_ = y_uniform
    clf.cutoff_scores_ = cutoff_scores
    clf.cutoff_ranks_ = cutoff_ranks

    return clf


def load_symptom_file(path, module):
    symptom_path = os.path.join(path, 'intermediate-files',
                                '{}-symptom.csv'.format(module))
    return pd.read_csv(symptom_path, index_col=0)


def main(module, smartva_repo, input_path, output_path=None):
    clf = train_smartva_classifier(smartva_repo, module)
    df = load_symptom_file(input_path, module)

    # Columns must be in the same order as the tariff matrix and all columns
    # must be present with valid values
    X = df.loc[:, clf.tariffs_.columns].fillna(0)

    restrictions = ian_riley_asthma_hack(df, RESTRICTIONS[module])
    import pdb; pdb.set_trace()
    results = clf.predict(X, ages=df.real_age, sexes=df.real_gender,
                          restrictions=restrictions)

    results.name = 'Prediction'
    results.index.name = 'sid'
    if output_path:
        output_name = '{}-predictions.csv'.format(module)
        results.to_csv(os.path.join(output_path, output_name), header=True)
    return results


def ian_riley_asthma_hack(symptoms, restrictions):
    restricted_symptoms = ['s99994', 's999979', 's7', 's55991', 's148', 's9999122', 's138', 's139', 's52', 's50', 's86', 's84']
    restricted = symptoms.loc[:, restricted_symptoms].any(1)
    restrictions['ad_hoc'] = [(4, restricted)]
    return restrictions


if __name__ == '__main__':
    module = 'adult'
    smartva_repo = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', '..', 'smartva')
    main(module, smartva_repo, sys.argv[1], sys.argv[2])
