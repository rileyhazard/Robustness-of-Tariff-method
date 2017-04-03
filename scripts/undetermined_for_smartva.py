import os
import glob

import pandas as pd


REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_DIR, 'data', 'redistribution')


def get_weights(module):
    weights = []
    undetermined = []
    for f in glob.glob(os.path.join(DATA_DIR, f'{module}_und*.csv')):
        params = f.strip('.csv').split('-')[-1]

        df = pd.read_csv(f)

        w_idx = ['iso3', 'age', 'sex', 'cause']
        w_cols = [*w_idx, 'weight']
        rename_w = {'weight': params}
        weights.append(df[w_cols].set_index(w_idx).rename(columns=rename_w))

        und = df[['cause', 'undetermined']].drop_duplicates() \
                .rename(columns={'undetermined': params})
        und = und.loc[und[params] != 0].set_index('cause').sort_index()
        undetermined.append(und)

    weights = pd.concat(weights, axis=1)
    undetermined = pd.concat(undetermined, axis=1).fillna(0)
    undetermined.index.name = 'cause'

    return weights, undetermined


def main():
    outdir = os.path.join(DATA_DIR, '_for_smartva')
    for module in ('adult', 'child', 'neonate'):
        weights, undetermined = get_weights(module)

        weights_fname = f'{module}_undetermined_weights.csv'
        weights.index.names = [*weights.index.names[:3], 'gs_text34']
        weights.to_csv(os.path.join(outdir, weights_fname))

        undeter_fname = f'{module}_undetermined_probs.csv'
        undetermined.to_csv(os.path.join(outdir, undeter_fname))


if __name__ == '__main__':
    main()
