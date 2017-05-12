import glob
import os

import pandas as pd

from tariff2 import REPO_DIR, MODULES
from tariff2.data.map_gbd_causes import CAUSE_MAP
from tariff2.tariff import TariffClassifier
from tariff2.loaders import get_cause_map
from tariff2.validation import (
    out_of_sample_accuracy,
    config_sss_model_selector,
)


def calc_gbd_cause_weights(module):
    """

    """
    if module not in MODULES:
        raise ValueError(f'Unknown module: "{module}"')

    gbd_data_dir = os.path.join(REPO_DIR, 'data', 'gbd')
    data_file_glob = os.path.join(gbd_data_dir, 'IHME-GBD_2015_DATA-*.csv')
    loc_filename = 'IHME_GBD_2015_LOCATION_HIERARCHIES_Y2016M12D01.csv'

    loc_hierarchy = pd.read_csv(os.path.join(gbd_data_dir, loc_filename))
    iso3s = dict(zip(loc_hierarchy.location_name, loc_hierarchy.location_code))

    df = pd.concat([pd.read_csv(f) for f in glob.glob(data_file_glob)])
    df.sex = df.sex.map({'Male': 1, 'Female': 2}).astype(int)
    df['iso3'] = df.location.map(iso3s)
    df.age = df.age.map(lambda x: x.split()[0])
    columns = ['iso3', 'age', 'sex', 'cause', 'val']
    df = df[columns]
    if df.isnull().any().any():
        raise ValueError

    nn_ages = {
        'adult': {'Early': -9, 'Late': -9, 'Post': -9},
        'child': {'Early': -9, 'Late': -9, 'Post': 0},
        'neonate': {'Early': 0, 'Late': 7, 'Post': -9},
    }
    ages = {
        'adult': list(range(10, 81, 5)),
        'child': [0, 1, 5, 10],
        'neonate': [0, 7],
    }

    df.age = df.age.replace(nn_ages[module]).astype(int)
    df = df.loc[df.age.isin(ages[module])]

    df.cause = df.cause.map(CAUSE_MAP[module])
    df = df.dropna().groupby(['iso3', 'age', 'sex', 'cause']).val.sum()

    agg = df.groupby(level=['iso3', 'cause']).sum().reset_index()
    agg['age'] = 99
    agg['sex'] = 3

    if module == 'neonate':
        idx = pd.MultiIndex.from_product([
            agg.iso3.unique(), [0, 99], [1, 2, 3], ['Stillbirth']
        ], names=['iso3', 'age', 'sex', 'cause'])
        sb = pd.DataFrame(index=idx, columns=['val']).reset_index()
    else:
        sb = pd.DataFrame()

    df = pd.concat([df.reset_index(), agg, sb])
    return df[columns].rename(columns={'val': 'gbd_csmf'})


def calc_probability_undetermined(X, y, module, n_splits=5, aggregation=None,
                                  subset=None, **kwargs):
    """

    """
    clf = TariffClassifier(**kwargs)
    sss = config_sss_model_selector(n_splits=n_splits)
    results = out_of_sample_accuracy(X, y, clf, sss, aggregate=aggregation,
                                     subset=subset)

    pred, *_ = results
    pred['undetermined'] = pred.prediction.isnull() | (pred.prediction == 'Undetermined')
    return pred.groupby(['split', 'actual']).undetermined.mean() \
               .groupby(level='actual').mean()


def calc_redistribution_weights(gbd_csmf, undetermined_prob):
    """

    """
    undetermined_prob.index.name = 'cause'
    df = gbd_csmf.merge(undetermined_prob.reset_index(), how='outer')
    df['weight'] = (df.gbd_csmf.fillna(df.undetermined) + df.undetermined) / 2
    df.weight = df.groupby(['iso3', 'age', 'sex']).weight \
                  .apply(lambda series: series/series.sum())
    return df.sort_values(['iso3', 'age', 'sex', 'cause'])
