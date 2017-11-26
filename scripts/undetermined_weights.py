from itertools import product
import os
import sys

import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tariff2 import MODULES, REPO_DIR
from tariff2.tariff import TariffClassifier
from tariff2.loaders import (
    get_X_y,
    get_smartva_config,
    get_cause_map,
    get_codebook,
)
from tariff2.redistribution import (
    calc_gbd_cause_weights,
    calc_probability_undetermined,
    calc_redistribution_weights,
)


def make_output_dir():
    path = os.path.join(REPO_DIR, 'data', 'redistribution')
    try:
        os.mkdir(path)
    except OSError:
        pass
    return path


def main(dataset, module, input_dir=None, n_splits=2, hce=True, short=True,
         subset=None, probs=None):
    output_dir = make_output_dir()
    instrument = 'short' if short else 'full'
    gbd_csmf = calc_gbd_cause_weights(module)

    if probs:
        undetermined_prob = pd.read_csv(probs, index_col=0).undetermined

    else:
        cb = get_codebook(f'{module}_symptom')
        hce_cols = np.full(len(cb), True, dtype=bool) if hce else (cb.hce == hce)
        cols = cb.loc[hce_cols & cb[instrument].astype(bool)].index

        X, y = get_X_y(dataset, module, input_dir)
        metadata_cols = ['age_', 'sex_', 'rules_']
        drop_cols = X.columns.difference(cols).difference(metadata_cols)
        X.loc[:, drop_cols] = 0   # keep but mask to avoid index errors

        cause_map = get_cause_map(module, 'smartva_text', 'smartva_reporting')
        cause_map[float('nan')] = 'Undetermined'
        kwargs = {
            'n_splits': n_splits,
            'aggregation': cause_map,
            'subset': subset,
            **get_smartva_config(module)
        }
        undetermined_prob = calc_probability_undetermined(X, y, module,
                                                          **kwargs)

    weights = calc_redistribution_weights(gbd_csmf, undetermined_prob)

    df = pd.DataFrame(list(product(
        weights.iso3.unique(),
        weights.age.unique(),
        [1, 2, 3],
        weights.cause.unique(),
    )), columns=['iso3', 'age', 'sex', 'cause'])
    df = df.loc[~(((df.age == 99) & (df.sex != 3)) |
                  ((df.sex == 3) & (df.age != 99)))]
    df = df.merge(weights, how='left').fillna(0)

    hce = int(hce)
    ss = '_s{}-{}'.format(*subset) if subset else ''
    filename = f'{module}_undetermined_weights-{instrument}_hce{hce}{ss}.csv'
    df.to_csv(os.path.join(output_dir, filename), index=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', choices=['phmrc', 'nhmrc'])
    parser.add_argument('module', choices=['adult', 'child', 'neonate'])
    parser.add_argument('--input_dir', help='Directory of previous Smartva '
                        'output. The symptoms files will be used.')
    parser.add_argument('--hce', action='store_true')
    parser.add_argument('--short', action='store_true')
    parser.add_argument('--n-splits', type=int, default=2)
    parser.add_argument(
        '--subset', default=None, type=int, nargs=2,
        help=('Define the range of splits implemented in this run. Pass two '
              'ints separated by a spaces. Numbers should range between 0 and '
              'splits minus 1'))
    parser.add_argument('--probs', help='Path to undetermined probabilities.')
    args = parser.parse_args()
    main(**vars(args))
