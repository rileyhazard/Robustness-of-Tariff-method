import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tariff2 import MODULES
from tariff2.ghdx import GHDX_CODEBOOK, GHDX_FILENAME, GHDX_DIR


GHDX_URL = ('http://ghdx.healthdata.org/sites/default/files/'
            'record-attached-files')


def download_ghdx_data():
    """Download PHMRC data and codebook from GHDx

    Data and codebook are saved with the original names in the ./data/ghdx
    subdirectory of the repo. The original codebook file from the GHDx is an
    excel file, but it is converted and saved as a csv.

    """
    filename = GHDX_CODEBOOK[:-4]   # remove '.csv'
    codebook = pd.read_excel(f'{GHDX_URL}/{filename}.xlsx')   # add '.xlsx'
    codebook.to_csv(os.path.join(GHDX_DIR, GHDX_CODEBOOK), encoding='utf-8',
                    index=False)
    out = [codebook]

    for module in MODULES:
        i = 2 if module == 'child' else 1
        filename = GHDX_FILENAME[:-4].format(module.upper(), i)  # remove 'csv'
        df = pd.read_stata(f'{GHDX_URL}/{filename}.dta',
                           convert_categoricals=False)
        df.to_csv(os.path.join(GHDX_DIR, f'{filename}.csv'), encoding='utf-8',
                  index=False)
        out.append(df)

    return df


if __name__ == '__main__':
    download_ghdx_data()
