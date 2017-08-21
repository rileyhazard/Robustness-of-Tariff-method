import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tariff2 import REPO_DIR
from tariff2 import tariff
from tariff2 import loaders


SMARTVA_DIR = os.path.join(os.path.dirname(REPO_DIR), 'smartva')


def get_data():
    module = 'adult'
    tariff_data = loaders.load_smartva_tariff_data(SMARTVA_DIR, module)

    tariffs = loaders.load_smartva_tariff_matrix(SMARTVA_DIR, module)
    tariffs.index = tariffs.index.map(tariff_data.CAUSES46.get)
    spurs = {tariff_data.CAUSES46[cause]: spurs
             for cause, spurs in tariff_data.SPURIOUS_ASSOCIATIONS.items()}
    tariffs = tariff.remove_spurious_associations(tariffs, spurs)
    tariffs = tariff.keep_top_symptoms(tariffs)
    tariffs = tariff.round_tariffs(tariffs)

    validated = loaders.load_smartva_validated_data(SMARTVA_DIR, module)
    uniform = validated.loc[np.repeat(*zip(*tariff_data.FREQUENCIES.items()))]
    drop_cols = validated.filter(regex='^gs_|^va+\d|site').columns
    symp = uniform.drop(drop_cols, axis=1).fillna(0).astype(int)

    # Only analyze shortened questionnaire
    short_drop = tariff_data.SHORT_FORM_DROP_LIST
    symp = symp.drop(short_drop, axis=1)
    tariffs = tariffs.drop(short_drop, axis=1)

    encode_causes = {v: k for k, v in tariff_data.CAUSES46.items()}
    cause_num = uniform.gs_text46.map(encode_causes).values - 1
    cutoff = tariff_data.CUTOFF_POS * 100
    scored = tariff.score_samples(symp, tariffs)
    _, cutoff_ranks = tariff.calc_cutoffs(scored, cause_num, cutoff)

    return tariffs, cutoff_ranks, scored, uniform.gs_text46


def predict():
    tariffs, cutoffs, scored, y = get_data()
    ranked = tariff.rank_samples(scored, scored)
    valid = tariff.mask_uncertain(scored, ranked, train_n=scored.shape[0],
                                  cutoffs=cutoffs, min_pct=18)
    return scored, valid


if __name__ == '__main__':
    scored, ranked = predict()
    scored.to_csv(os.path.join(REPO_DIR, 'data', 'uniform-scored.csv'))
    ranked.to_csv(os.path.join(REPO_DIR, 'data', 'uniform-ranked.csv'))
