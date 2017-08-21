import os

import pandas as pd

from tariff2 import REPO_DIR, MODULES, getters
from tariff2.validation import (
    out_of_sample_accuracy,
    config_sss_model_selector,
)
from tariff2.tariff import TariffClassifier
from tariff2.utils import union_NDFrame_indicies


SRC_DATA_DIR = os.path.join(REPO_DIR, 'src', 'data')
CUTOFFS_PATH = os.path.join(SRC_DATA_DIR, 'smartva_cutoffs.yml')
SPURIOUS_PATH = os.path.join(SRC_DATA_DIR, 'smartva_spurious.yml')
RESTRICTIONS_PATH = os.path.join(SRC_DATA_DIR, 'smartva_restrictions.yml')
CENSORING_PATH = os.path.join(SRC_DATA_DIR, 'smartva_censoring.yml')


def get_phmrc(module):
    data_dir = os.path.join(REPO_DIR, 'data', 'smartva_output',
                            'phmrc_short-3')
    gs = getters.get_gold_standard('phmrc', module)
    gs = gs.gs_text46
    return gs, data_dir


def get_combined(module):
    data_dir = os.path.join(REPO_DIR, 'data', 'smartva_output',
                            'gs_full')
    gs_path = os.path.join(REPO_DIR, 'external', 'data_release',
                           'gs_full.csv')
    df = pd.read_csv(gs_path, index_col=0)
    gs = df.loc[df.gs_analytic != 'Neonatal tetanus', 'gs_analytic']
    return gs, data_dir


def analyze(module, loader):

    cutoffs = getters.get_metadata(CUTOFFS_PATH, module)
    spurious = getters.get_metadata(SPURIOUS_PATH, module)
    restrictions = getters.get_metadata(RESTRICTIONS_PATH, module)
    censoring = getters.get_metadata(CENSORING_PATH, module)

    causes = getters.get_cause_map(module, 'smartva_text', 'smartva_reporting')
    num_to_causes = getters.get_cause_map(module, 'smartva', 'smartva_text')

    metadata = ('age', 'sex', 'rules')
    renames = {
        'age': 'age_',
        'sex': 'sex_',
        'cause': 'rules',
        'real_age': 'age',
        'real_gender': 'sex',
    }

    gs, data_dir = loader(module)

    df = getters.get_smartva_symptom_file(data_dir, module)
    df = df.rename(columns=renames)
    df.rules = df.rules.map(num_to_causes)

    if 'restricted' in df:
        df.drop('restricted', axis=1, inplace=True)

    cols = list(metadata) + df.drop(list(metadata), axis=1).columns.tolist()
    df = df[cols]

    df, gs = union_NDFrame_indicies(df, gs)

    ms = config_sss_model_selector(n_splits=30)
    clf = TariffClassifier(tariffs_ui=99, spurious_associations=spurious,
                           restrictions=restrictions, censoring=censoring,
                           metadata=metadata, **cutoffs)

    results = out_of_sample_accuracy(df, gs, clf, ms, aggregate=causes)
    return results


def main():
    outdir = os.path.join(REPO_DIR, 'data', 'combined_performance')
    for loader in [get_phmrc, get_combined]:
        dataset = loader.__name__[4:]
        for module in MODULES:
            results = analyze(module, loader)
            for i, name in enumerate(['pred', 'csmf', 'ccc', 'accuracy']):
                filename = '{}-{}-{}.csv'.format(dataset, module, name)
                results[i].to_csv(os.path.join(outdir, filename), index=False)


if __name__ == '__main__':
    main()
