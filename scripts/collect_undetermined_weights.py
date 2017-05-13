import glob
import itertools
import os

import pandas as pd


REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(REPO_DIR, 'data', 'redistribution')
OUTDIR = os.path.join(PATH, 'undetermined')
#MODULES = ('adult', 'child', 'neonate')
MODULES = ['neonate']
INSTRUMENTS = ('short', 'full')
HCES = (0, 1)
FILENAME = '{}_undetermined_weights-{}_hce{}'


def make_dir(path):
    try:
        os.mkdir(path)
    except OSError:
        pass


def collect():
    make_dir(OUTDIR)
    for params in itertools.product(MODULES, INSTRUMENTS, HCES):
        fname = FILENAME.format(*params)
        dfs = []
        for i, f in enumerate(glob.glob(os.path.join(PATH, fname + '_s*.csv'))):
            df = pd.read_csv(f)
            causes = df.cause.unique()
            df = df.loc[df.undetermined != 0, ['cause', 'undetermined']]
            df = df.drop_duplicates()
            df = df.set_index('cause').loc[causes].fillna(0).reset_index()
            dfs.append(df)
        df = pd.concat(dfs).groupby('cause').mean().reset_index()
        df.to_csv(os.path.join(OUTDIR, fname + '.csv'), index=False)


if __name__ == '__main__':
    collect()
