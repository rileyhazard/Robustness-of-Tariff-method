import os

import pandas as pd
import urllib2


GHDX_CODEBOOK = 'IHME_PHMRC_VA_DATA_CODEBOOK_Y2013M09D11_0.csv'
GHDX_FILENAME = 'IHME_PHMRC_VA_DATA_{}_Y2013M09D11_0.csv'
MODULES = ['adult', 'child', 'neonate']


def download_ghdx_data(outdir=None):
    """Download PHMRC data and codebook from GHDx

    Data and codebook are saved with the original names in the specified
    output directory. The original codebook file from the GHDx is an excel
    file, but it is saved as a csv.

    Args:
        outdir (str): directory to save files. If None, files are not saved.

    Returns:
        codebook (dataframe)
        adult_data (dataframe)
        child_data (dataframe)
        neonate_data (dataframe)
    """
    out = []
    ghdx_url = ('http://ghdx.healthdata.org/sites/default/files/'
                'record-attached-files')

    # The codebook is an excel file instead of a csv on the GHDx
    url = '{ghdx}/{cb}.xlsx'.format(ghdx=ghdx_url, cb=GHDX_CODEBOOK[:-4])
    response = urllib2.urlopen(url)
    xls = pd.ExcelFile(response)
    codebook = xls.parse(xls.sheet_names[0])
    out.append(codebook)
    if outdir:
        filepath = os.path.join(outdir, GHDX_CODEBOOK)
        codebook.to_csv(filepath, encoding='utf-8', index=False)

    for module in ['ADULT', 'CHILD', 'NEONATE']:
        f = GHDX_FILENAME.format(module.upper())
        url = '{ghdx}/{f}'.format(ghdx=ghdx_url, f=f)
        response = urllib2.urlopen(url)
        df = pd.read_csv(response)
        out.append(df)
        if outdir:
            df.to_csv(os.path.join(outdir, f), index=False)

    return tuple(out)


def save_ghdx_gold_standards(adult, child, neonate, outfile):
    data = [adult, child, neonate]
    gs_cols = ['site', 'module', 'gs_text46', 'gs_level']

    # Nobody cares about the 11 neonate causes, only the 6
    neonate.gs_text46 = neonate.gs_text34

    gs = []
    for df in data:
        # `newid` is a incrementor in each file. Make it a unique index by
        # concatenating the module and incrementor
        df['sid'] = df.module + df.newid.astype(str)
        df = df.set_index('sid')
        df.module = df.module.str.lower()
        df.gs_level = df.gs_level.str.lstrip('GS Level ')
        gs.append(df.loc[:, gs_cols])
    gs = pd.concat(gs)
    gs.to_csv(outfile)
    return gs


def load_local_ghdx_data(directory=None):
    """Load GHDx PHMRC files from a local directory

    Data and codebook should be saved with the original names and as csvs.

    Args:
        directory (str): path to directory. Defaults to ${repo}/data/ghdx

    Returns:
        codebook (dataframe)
        adult_data (dataframe)
        child_data (dataframe)
        neonate_data (dataframe)
    """
    if not directory:
        filepath = os.path.abspath(os.path.dirname(__file__))
        directory = os.path.join(filepath, '..', 'data', 'ghdx')

    out = [pd.read_csv(os.path.join(directory, GHDX_CODEBOOK))]

    for module in MODULES:
        filename = GHDX_FILENAME.format(module.upper())
        df = pd.read_csv(os.path.join(directory, filename))
        df['sid'] = df.module + df.newid.astype(str)
        df = df.set_index('sid')
        out.append(df)

    return tuple(out)


def main():
    repo = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    out = download_ghdx_data(os.path.join(repo, 'data', 'ghdx'))
    codebook, adult, child, neonate = out
    gs_path = os.path.join(repo, 'data', 'gold_standards', 'phmrc_gs.csv')
    gs = save_ghdx_gold_standards(adult, child, neonate, gs_path)
    return gs


if __name__ == '__main__':
    main()
