import os

import pandas as pd

from getters import REPO_DIR, get_smartva_symptoms, get_codebook


def rootj():
    for path in ['/home/j', 'J:', 'J:/']:
        if os.path.exists(path):
            return path
    else:
        raise OSError("You're wandering around in a world without J...")


NHMRC_DATA_DIR = os.path.join(rootj(), 'LIMITED_USE', 'PROJECT_FOLDERS',
                              'NHMRC_VA', 'external_va_2015', 'NHMRC', 'Data')
MODULES = ['adult', 'child', 'neonate']


def load_data(version=None, instrument='full'):
    if not version:
        version = []
        for path in os.listdir(NHMRC_DATA_DIR):
            try:
                v = int(path.split(os.path.sep)[-1].lstrip('version'))
                version.append(v)
            except ValueError:
                pass
        version = max(version)
        print 'Using version {}'.format(version)

    path = os.path.join(NHMRC_DATA_DIR, 'version{}'.format(version), 'output',
                        '{}_comm_{}')
    sites = ['BGD', 'Bohol', 'PNG']

    out = {}
    for mod in MODULES:
        data = [get_smartva_symptoms(path.format(site, instrument), mod)
                for site in sites]
        out[mod] = pd.concat(data)
    return out


def main(version=None, instrument='full'):
    data = load_data(version, instrument)
    cb = {mod: get_codebook('{}_symptom.csv'.format(mod)) for mod in MODULES}
    endorsements = []
    for mod in MODULES:
        endorse = pd.concat([data[mod].mean(), cb[mod].question], axis=1)
        endorse.index.name = 'predictor'
        endorse.columns = ['endorsements', 'question']
        endorse['module'] = mod
        endorsements.append(endorse)

    df = pd.concat(endorsements).reset_index()
    df = df.loc[df.endorsements > 0,
                ['module', 'predictor', 'question', 'endorsements']]

    filename = 'NHMRC_community_endorsments_{}.xlsx'.format(instrument)
    outfile = os.path.join(REPO_DIR, 'external', filename)
    pd.formats.format.header_style = None
    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
    workbook = writer.book

    pct_fmt = workbook.add_format({'num_format': '0.0%'})

    df.to_excel(writer, sheet_name='Endorsements', index=False)
    sheet = writer.sheets['Endorsements']
    sheet.autofilter(0, 0, df.shape[0], df.shape[1] - 1)
    sheet.freeze_panes(1, 0)
    sheet.set_column(2, 2, 102.00)
    sheet.set_column(3, 3, 13.29, pct_fmt)


if __name__ == '__main__':
    main()
