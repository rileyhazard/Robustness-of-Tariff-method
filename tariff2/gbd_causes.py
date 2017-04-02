import glob
import os

import pandas as pd

from tariff2 import REPO_DIR
from tariff2.data.map_gbd_causes import CAUSE_MAP


GBD_DATA_DIR = os.path.join(REPO_DIR, 'data', 'gbd')


def load_gbd_data():
    path = os.path.join(GBD_DATA_DIR, 'IHME-GBD_2015_DATA-*.csv')
    return pd.concat([pd.read_csv(f) for f in glob.glob(path)])


def load_location_hierarchy():
    filename = 'IHME_GBD_2015_LOCATION_HIERARCHIES_Y2016M12D01.csv'
    return pd.read_csv(os.path.join(GBD_DATA_DIR, filename))


def clean_gbd_data():
    loc_hierarchy = load_location_hierarchy()
    iso3s = dict(zip(loc_hierarchy.location_name, loc_hierarchy.location_code))

    df = load_gbd_data()
    df.sex = df.sex.map({'Male': 1, 'Female': 2}).astype(int)
    df['iso3'] = df.location.map(iso3s)
    df.age = df.age.map(lambda x: x.split()[0])

    cols = ['iso3', 'age', 'sex', 'cause', 'val']
    if df[cols].isnull().any().any():
        raise ValueError

    return df[cols]


def calc_gbd_cause_fractions():
    df = clean_gbd_data()
    idx_cols = ['iso3', 'age', 'sex', 'cause']
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

    weights = {}
    for module, causes in CAUSE_MAP.items():
        mapped = df.copy()

        mapped.age = mapped.age.replace(nn_ages[module]).astype(int)
        mapped = mapped.loc[mapped.age.isin(ages[module])]

        mapped.cause = mapped.cause.map(causes)
        mapped = mapped.dropna().groupby(idx_cols).val.sum().reset_index()

        agg = mapped.groupby(['iso3', 'cause']).sum()
        agg['age'] = 99
        agg['sex'] = 3

        weights[module] = pd.concat([mapped, agg]).set_index(idx_cols)

    return weights


def main():
    csmf = calc_gbd_cause_fractions()
    for module, df in csmf.items():
        df.to_csv()


if __name__ == '__main__':
    main()
