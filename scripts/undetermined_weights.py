from itertools import product
import os
import sys

import pandas as pd

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


def main(dataset, module, input_dir, n_splits=2, hce=True, short=True):
    output_dir = make_output_dir()
    gbd_csmf = calc_gbd_cause_weights(module)

    cb = get_codebook(f'{module}_symptom')
    instrument = 'short' if short else 'full'
    cols = cb.loc[(cb.hce == hce) & cb[instrument].astype(bool)].index

    X, y = get_X_y(dataset, module, input_dir)
    drop_cols = X.columns.difference(cols)
    X.loc[:, drop_cols] = 0   # keep but mask to avoid index errors

    cause_map = get_cause_map(module, 'smartva_text', 'smartva_reporting')
    cause_map[float('nan')] = 'Undetermined'
    kwargs = {
        'n_splits': n_splits,
        'aggregation': cause_map,
        **get_smartva_config(module)
    }
    undetermined_prob = calc_probability_undetermined(X, y, module, **kwargs)

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
    filename = f'{module}_undetermined_weights-{instrument}_hce{hce}.csv'
    df.to_csv(os.path.join(output_dir, filename), index=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', choices=['phmrc', 'nhmrc'])
    parser.add_argument('module', choices=['adult', 'child', 'neonate'])
    parser.add_argument('input_dir', help='Directory previous Smartva output')
    parser.add_argument('--hce', action='store_true')
    parser.add_argument('--short', action='store_true')
    parser.add_argument('--n-splits', type=int, default=2)
    args = parser.parse_args()
    main(**vars(args))
