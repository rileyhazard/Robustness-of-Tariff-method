import os
import sys

import pandas as pd
import yaml

from tariff2 import MODULES, REPO_DIR
from tariff2.utils import union_NDFrame_indicies


def get_gold_standard(dataset, module=None):
    if dataset in ['phmrc', 'nhmrc']:
        filename = '{}_gs.csv'.format(dataset)
    else:
        raise ValueError("Unknown dataset '{}'".format(dataset))
    if module and module.lower() not in MODULES:
        raise ValueError("Unknown module '{}'".format(module))

    gs_path = os.path.join(REPO_DIR, 'data', 'gold_standards', filename)

    # NHMRC has numeric SIDs with leading zeros. Read in 'sid' as a string.
    gs = pd.read_csv(gs_path, dtype={'sid': 'str'}).set_index('sid')

    if module:
        gs = gs.loc[gs.module == module]
    return gs


def get_codebook(codebook):
    if not codebook.endswith('.csv'):
        codebook = '{}.csv'.format(codebook)
    return pd.read_csv(os.path.join(REPO_DIR, 'codebooks', codebook),
                       index_col=0)


def get_cause_map(module, src, target):
    df = pd.read_csv(os.path.join(REPO_DIR, 'codebooks', 'cause_map.csv'))
    df = df.loc[df.module == module]
    return dict(zip(df[src], df[target]))


def get_metadata(paths, modules=None, keys=None):
    if isinstance(paths, str):
        paths = [paths]

    if isinstance(modules, str):
        modules = [modules]
    elif modules is None:
        modules = MODULES

    if isinstance(keys, str):
        keys = [keys]

    yamls = []
    for path in paths:
        with open(path, 'r') as f:
            yamls.append(yaml.load(f))

    metadata = {module: dict() for module in modules}
    for yml in yamls:
        for module in modules:
            if module not in yml:
                continue
            for key in yml[module]:
                if keys is None or key in keys:
                    metadata[module].update(yml[module])

    if keys is not None and len(keys) == 1:
        metadata = {module: metadata[module].get(keys[0], {})
                    for module in modules}
    if len(modules) == 1:
        if modules[0] in metadata:
            metadata = metadata[modules[0]]
        else:
            metadata = dict()
    return metadata


def get_smartva_presymptom_file(path, module):
    path = os.path.join(path, 'intermediate-files',
                        '{}-presymptom.csv'.format(module))
    return pd.read_csv(path, dtype={'sid': 'str'}).set_index('sid')


def get_smartva_symptom_file(path, module):
    path = os.path.join(path, 'intermediate-files',
                        '{}-symptom.csv'.format(module))
    df = pd.read_csv(path, dtype={'sid': 'str'}).set_index('sid')

    # There's a bug in SmartVA which leads to duplicate age columns in
    # the neonate module
    if 'age.1' in df.columns:
        df = df.drop('age.1', axis=1)

    return df


def get_smartva_ranks_file(path, module):
    path = os.path.join(path, 'intermediate-files',
                        '{}-tariff-ranks.csv'.format(module))
    df = pd.read_csv(path, dtype={'sid': 'str'}).set_index('sid')
    df.columns = df.columns.map(int)
    return df


def get_smartva_predictions(path, module, rules=True, cause_map=None):

    def best_ranked(series):
        if len(series.unique()) > 1:
            return series.sort_values().first_valid_index()
        else:
            return float('nan')

    ranks = get_smartva_ranks_file(path, module)
    prediction = ranks.apply(best_ranked, axis=1).fillna(0)
    if rules:
        symptom = get_smartva_symptom_file(path, module)
        rules = symptom.cause
        prediction.loc[rules.notnull()] = rules.loc[rules.notnull()]

    if cause_map:
        prediction = prediction.replace(cause_map)

    return prediction


def get_smartva_symptoms(path, module):
    symptoms = get_smartva_symptom_file(path, module)
    non_binary_cols = ['cause', 'real_age', 'real_gender', 'restricted']
    non_binary_cols = symptoms.columns.intersection(non_binary_cols)
    return symptoms.drop(non_binary_cols, axis=1).fillna(0).astype(int)


def load_smartva_tariff_data(path, module):
    if module not in ['adult', 'child', 'neonate']:
        raise ValueError('Unknown module: "{}"'.format(module))
    if not os.path.exists(path):
        raise ValueError('Path not found: "{}"'.format(path))

    sys.path.insert(0, path)
    if module == 'adult':
        from smartva.data import adult_tariff_data as tariff_data
    elif module == 'child':
        from smartva.data import child_tariff_data as tariff_data
    elif module == 'neonate':
        from smartva.data import neonate_tariff_data as tariff_data
    sys.path.remove(path)

    return tariff_data


def load_smartva_tariff_matrix(path, module):
    matrix_path = os.path.join(path, 'smartva', 'data',
                               'tariffs-{}.csv'.format(module))
    df = pd.read_csv(matrix_path, index_col=0)
    df.index = df.index.str.lstrip('cause').astype(int)
    return df


def load_smartva_validated_data(path, module):
    path = os.path.join(path, 'smartva', 'data',
                        'validated-{}.csv'.format(module))
    return pd.read_csv(path, dtype={'sid': 'str'}).set_index('sid')


def get_smartva_config(module):
    """Get a dictionary of kwargs to configure Tariff to act like Smartva.

    Args:
        module (str): 'adult', 'child' or 'neonate'

    Returns:
        (dict)
    """
    def path(x):
        return os.path.join(REPO_DIR, 'tariff2', 'data', f'smartva_{x}.yml')

    return {
        'tariffs_ui': 99,
        'metadata': ('age_', 'sex_', 'rules_'),
        **get_metadata(path('spurious'), module),
        **get_metadata(path('restrictions'), module),
        **get_metadata(path('censoring'), module),
        **get_metadata(path('cutoffs'), module),
    }


def get_X_y(dataset, module, path):
    """Load the symptoms and gold standards for a given dataset.

    Args:
        datasets (str): 'phmrc', 'nhmrc', 'combine'

    Returns:
        X (dataframe): samples by symptoms matrix with prepended metadata
            columns (age_, sex_, rules_)
        y (series): gold standard cause for each sample

    """
    X = get_smartva_symptom_file(path, module)
    y = get_gold_standard(dataset, module).gs_text46

    X, y = union_NDFrame_indicies(X, y)

    drop_cols = X.columns.intersection(['restricted'])
    metadata_cols = ['age_', 'sex_', 'rules_']
    renames = dict(zip(['real_age', 'real_gender', 'cause'], metadata_cols))
    X = X.rename(columns=renames).drop(drop_cols, axis=1)

    cause_map = get_cause_map(module, 'smartva', 'smartva_text')
    X.rules_ = X.rules_.replace(cause_map)

    symp_cols = X.columns.drop(metadata_cols)
    X[symp_cols] = X[symp_cols].fillna(0)

    col_order = [*metadata_cols, *symp_cols]
    X = X[col_order]

    return X, y
