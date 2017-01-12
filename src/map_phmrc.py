import os

import numpy as np
import pandas as pd
import urllib2

from mapping import *

MODULES = ['adult', 'child', 'neonate']
GHDX_CODEBOOK = 'IHME_PHMRC_VA_DATA_CODEBOOK_Y2013M09D11_0.csv'
GHDX_FILENAME = 'IHME_PHMRC_VA_DATA_{}_Y2013M09D11_0.csv'


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

    for module in MODULES:
        f = GHDX_FILENAME.format(module.upper())
        url = '{ghdx}/{f}'.format(ghdx=ghdx_url, f=f)
        response = urllib2.urlopen(url)
        df = pd.read_csv(response)
        out.append(df)
        if outdir:
            df.to_csv(os.path.join(outdir, f), index=False)

    return tuple(out)


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
        out.append(df)

    return tuple(out)


def prep_codebook(codebook):
    """Clean the codebock and add information about column type"""
    cb = codebook.set_index('variable')

    cb.loc[cb.coding.notnull(), 'type'] = 'categorical'
    cb.loc[cb.coding.isnull(), 'type'] = 'numeric'
    cb.loc[cb.index.str.startswith('word_'), 'type'] = 'word'
    cb.loc[['site', 'g2_01', 'g2_02'], 'type'] = 'info'

    # Some numeric variables have a sentinel value for missing which appears
    # in the coding coding. This value is always a set of 9s as "Don't Know"
    # Since this is the only coding it appears at the begining of the string
    num_with_dk = cb.coding.str.contains('^9+ "Don\'t Know"').fillna(False)
    cb.loc[num_with_dk, 'type'] = 'numeric'

    # These regexs are designned to NOT match the string '[specify unit]',
    # which is a numeric encoding of the unit
    freetext_re = 'specified|, specify|from the certificate|Record from where'
    cb.loc[cb.question.str.contains(freetext_re), 'type'] = 'freetext'

    # This columns is not actually in the data
    cb.drop('gs_diagnosis', inplace=True)

    # The codebook is missing a space between the 1 and "Grams" which causes
    # the mapping from coding function to fail
    cb.loc['c1_08a', 'coding'] = ('1 "Grams" 8 "Refused to Answer" '
                                  '9 "Don\'t Know"')

    return cb


def map_short_form_freetext(mapping):
    for short, full in ODK_FREETEXT_SHORT_TO_LONG.items():
        if not short.startswith(module):
            continue

def map_to_odk(df, cb):
    # Some numeric columns contain a sentinel value for missing which was
    # encoded as the string "Don't Know" in the data. This forces the column
    # to be read as an object dytpe instead of a float
    num_cols = filter(df.columns.__contains__,
                      cb.loc[cb.type == 'numeric'].index)
    df.loc[:, num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')

    # ODK only has a single "select one" question for location of belly pain.
    # Upper belly pain is not relevant for tariff, only lower belly pain is
    # important. If lower belly pain is in the secondary belly pain location
    # it should be moved to the variable which is mappped to the ODK variable.
    if 'a2_63_1' in df.columns and 'a2_63_2' in df.columns:
        df.loc[df.a2_63_2 == 'Lower belly', 'a2_63_1'] = 'Lower belly'

    # Create the injury screening questions. The dataset has an indicator
    # for "Experienced no injuries". If this is endorsed than the injury
    # screening question should not be endorsed
    if 'a5_01_8' in df.columns:
        df['adult_5_1'] = df.a5_01_8.map(lambda x: int(x != 'Yes'))
    if 'c4_47_11' in df.columns:
        df['child_4_47'] = df.c4_47_11.map(lambda x: int(x != 'Yes'))

    # The PHMRC dataset has two variables for "other specified" rash location
    # for adults. These should be combined into a single string in the first
    # column which is mapped to the ODK variable
    if 'a2_09_1b' in df.columns and 'a2_09_2b' in df.columns:
        df.a2_09_1b = df[['a2_09_1b', 'a2_09_2b']].apply(concat_str, axis=1)

    # Categorical columns contain their labels instead of the encoded numeric
    # value. These should be encoded.
    code_group = cb.loc[cb.type == 'categorical'].groupby('coding')
    for coding, cols in code_group.groups.items():
        cols = filter(df.columns.__contains__, cols)
        mapping = mapping_from_coding(coding)
        encoded = df[cols].replace(mapping)
        encoded = encoded.apply(pd.to_numeric, errors='coerce')
        encoded[~encoded.isin(mapping.values())] = np.nan
        df.loc[:, cols] = encoded.fillna(lookup_default(coding))

    # Duration variables in the data files are in a single variable and have
    # been converted to days. ODK is expecting a variable which says the unit
    # a variable with the value in that unit.
    duration_scalar = {2: 1 / float(30), 3: 1 / float(7), 4: 1, 5: 24}
    for orig_col, (unit_col, val_col, unit_val) in DURATION_VARS.items():
        if orig_col in df.columns:
            df[unit_col] = unit_val
            df[val_col] = df[orig_col] * duration_scalar[unit_val]

    # ODK encodes multiselect answers as strings of space separated ints
    # The datasets split multiselects into series of columns. There are two
    # formats: 1) multiple encoded categoricals and 2) binarized
    for target, (sources, missing) in MULTISELECT_CATEGORICAL_VARS.items():
        if filter(df.columns.__contains__, sources):
            df[target] = df[sources].apply(concat_encoded, missing=missing,
                                           axis=1)
    for target, mapping in MULTISELECT_BINARY_VARS.items():
        cols = filter(df.columns.__contains__, mapping.keys())
        if cols:
            df[target] = df[cols].apply(concat_binary, mapping=mapping, axis=1)

    # Multiselect dates (a6_06, c5_06) not used in Smartva...

    # Map the column names to ODK
    df = df.rename(columns=VAR_CONVERSION_MAP)

    # PHMRC data asked the question about injuries in a way that elicitted
    # responses about any injury ever, not just injuries pertaining to the
    # death, as was intended. Injuries which occured more than 30 days before
    # the death are not likely related to the death and should be removed
    if 'adult_5_2'in df.columns and 'adult_5_5b' in df.columns:
        mask = df.adult_5_5b > 30
        df.loc[mask, 'adult_5_1'] = 0   # screening question
        df.loc[mask, 'adult_5_2'] = ''  # list of injuries
        df.loc[mask, 'adult_5_5b'] = 0  # duration
    if 'child_4_48' in df.columns and 'child_4_50b' in df.columns:
        mask = df.child_4_50b > 30
        df.loc[mask, 'child_4_47'] = 0   # screening question
        df.loc[mask, 'child_4_48'] = ''  # list of injuries
        df.loc[mask, 'child_4_50b'] = 0  # duration

    # Create age variables from ODK ages columns
    df['agedays'] = df.apply(calc_agedays, vars=ODK_AGE_VARS, axis=1)
    df['gen_5_4d'] = df.apply(calc_agegroup, vars=ODK_AGE_VARS, axis=1)

    # Combine words into dummy freetext
    freetext = df.filter(like="word_").apply(combine_freetext, axis=1)
    for module, var in FREETEXT_VARS.items():
        df.loc[df.module.str.lower() == module, var] = freetext

    # Map to the short form freetext variables
    for short, full in ODK_FREETEXT_SHORT_TO_LONG.items():
        cols = df.columns.intersection(['word_{}'.format(w) for w in full])
        if cols.any():
            df[short] = df.loc[:, cols].all(1).astype(int)
        else:
            df[short] = 0

    # Order columns, drop unused columns, and create missing columns
    odk_codebook = get_codebook('odk')
    df = df.reset_index().loc[:, odk_codebook.index].fillna('')

    # Some numeric columns, including data fragments, need to be encoded as
    # ints. Smartva cannot handle string floats (e.g. '7.0').
    df = df.fillna('').applymap(infer_dtype).astype(str)
    df = df.applymap(lambda x: x[:-2] if x.endswith('.0') else x)
    return df


def main(directory=None, update_ghdx=False):
    filepath = os.path.abspath(os.path.dirname(__file__))
    if not directory:
        directory = os.path.join(filepath, '..', 'data', 'ghdx')

    files = [os.path.join(directory, GHDX_CODEBOOK)]
    files.extend([os.path.join(GHDX_FILENAME.format(module.upper()))
                  for module in MODULES])

    if update_ghdx or not all(map(os.path.exists, files)):
        codebook, adult, child, neonate = download_ghdx_data(directory)
    else:
        codebook, adult, child, neonate = load_local_ghdx_data()

    outdir = os.path.join(filepath, '..', 'data')

    data = [adult, child, neonate]
    gs = []
    gs_cols = ['gs_text34', 'va34', 'gs_text46', 'va46']
    for df in data:
        # newid is a incrementor in each file.
        # Make an index unique across the different modules
        df['sid'] = df.module + df.newid.astype(str)
        df = df.set_index('sid')
        gs.append(df.loc[:, gs_cols])
    gs = pd.concat(gs)
    gs.to_csv(os.path.join(outdir, 'gold_standards', 'phmrc_gs.csv'))

    cb = prep_codebook(codebook)
    df = pd.concat([map_to_odk(df, cb) for df in data])

    odk_codebook = get_codebook('odk')

    full = df.copy()
    full.loc[:, odk_codebook.loc[odk_codebook.short_only == 1].index] = ''
    full.to_csv(os.path.join(outdir, 'odk', 'phmrc_full.csv'), index=False)

    short = df.copy()
    short.loc[:, odk_codebook.loc[odk_codebook.long_only == 1].index] = ''
    short.to_csv(os.path.join(outdir, 'odk', 'phmrc_short.csv'), index=False)

    return df


ODK_AGE_VARS = ['gen_5_4a', 'gen_5_4b', 'gen_5_4c']

VAR_CONVERSION_MAP = {
    'sid': 'sid',
    'g2_01': 'gen_2_1',
    'g2_02': 'gen_2_2a',
    'g3_01': 'gen_3_1',
    'g4_02': 'gen_4_2',
    'g4_03a': 'gen_4_3',
    'g4_04': 'gen_4_4',
    'g4_05': 'gen_4_5',
    'g4_06': 'gen_4_6',
    'g4_07': 'gen_4_7',
    'g4_08': 'gen_4_8',
    'g5_01d': 'gen_5_1c',
    'g5_01m': 'gen_5_1b',
    'g5_01y': 'gen_5_1a',
    'g5_02': 'gen_5_2',
    'g5_03d': 'gen_5_3c',
    'g5_03m': 'gen_5_3b',
    'g5_03y': 'gen_5_3a',
    'g5_04a': 'gen_5_4a',
    'g5_04b': 'gen_5_4b',
    'g5_04c': 'gen_5_4c',
    'g5_05': 'gen_5_5',
    'g5_06a': 'gen_5_6',
    'g5_07': 'gen_5_7',
    'g5_08': 'gen_5_8',

    'a1_01_1': 'adult_1_1a',
    'a1_01_2': 'adult_1_1b',
    'a1_01_3': 'adult_1_1c',
    'a1_01_13': 'adult_1_1d',
    'a1_01_5': 'adult_1_1e',
    'a1_01_6': 'adult_1_1f',
    'a1_01_7': 'adult_1_1g',
    'a1_01_8': 'adult_1_1h',
    'a1_01_9': 'adult_1_1i',
    'a1_01_10': 'adult_1_1j',
    'a1_01_11': 'adult_1_1k',
    'a1_01_12': 'adult_1_1l',
    'a1_01_4': 'adult_1_1m',
    'a1_01_14': 'adult_1_1n',

    'a2_02': 'adult_2_2',
    'a2_04': 'adult_2_4',
    'a2_05': 'adult_2_5',
    'a2_06': 'adult_2_6',
    'a2_07': 'adult_2_7',
    'a2_09_1b': 'adult_2_9a',
    'a2_10': 'adult_2_10',
    'a2_11': 'adult_2_11',
    'a2_12': 'adult_2_12',
    'a2_13': 'adult_2_13',
    'a2_14': 'adult_2_14',
    'a2_16': 'adult_2_16',
    'a2_17': 'adult_2_17',
    'a2_18': 'adult_2_18',
    'a2_19': 'adult_2_19',
    'a2_20': 'adult_2_20',
    'a2_21': 'adult_2_21',
    'a2_23': 'adult_2_23',
    'a2_25': 'adult_2_25',
    'a2_27': 'adult_2_27',
    'a2_29': 'adult_2_29',
    'a2_30': 'adult_2_30',
    'a2_31': 'adult_2_31',
    'a2_32': 'adult_2_32',
    'a2_34': 'adult_2_34',
    'a2_35': 'adult_2_35',
    'a2_36': 'adult_2_36',
    'a2_38': 'adult_2_38',
    'a2_40': 'adult_2_40',
    'a2_42': 'adult_2_42',
    'a2_43': 'adult_2_43',
    'a2_44': 'adult_2_44',
    'a2_45': 'adult_2_45',
    'a2_46a': 'adult_2_46',
    'a2_46b': 'adult_2_46a',
    'a2_47': 'adult_2_47',
    'a2_49': 'adult_2_49',
    'a2_50': 'adult_2_50',
    'a2_51': 'adult_2_51',
    'a2_52': 'adult_2_52',
    'a2_53': 'adult_2_53',
    'a2_55': 'adult_2_55',
    'a2_56': 'adult_2_56',
    'a2_57': 'adult_2_57',
    'a2_59': 'adult_2_59',
    'a2_60': 'adult_2_60',
    'a2_61': 'adult_2_61',
    'a2_63_1': 'adult_2_63',
    'a2_64': 'adult_2_64',
    'a2_66': 'adult_2_66',
    'a2_67': 'adult_2_67',
    'a2_69': 'adult_2_69',
    'a2_71': 'adult_2_71',
    'a2_72': 'adult_2_72',
    'a2_74': 'adult_2_74',
    'a2_75': 'adult_2_75',
    'a2_77': 'adult_2_77',
    'a2_78': 'adult_2_78',
    'a2_80': 'adult_2_80',
    'a2_81': 'adult_2_81',
    'a2_82': 'adult_2_82',
    'a2_84': 'adult_2_84',
    'a2_85': 'adult_2_85',
    'a2_87_10b': 'adult_2_87a',

    'a3_01': 'adult_3_1',
    'a3_02': 'adult_3_2',
    'a3_03': 'adult_3_3',
    'a3_04': 'adult_3_4',
    'a3_05': 'adult_3_5',
    'a3_06': 'adult_3_6',
    'a3_07': 'adult_3_7',
    'a3_09': 'adult_3_9',
    'a3_10': 'adult_3_10',
    'a3_12': 'adult_3_12',
    'a3_13': 'adult_3_13',
    'a3_14': 'adult_3_14',
    'a3_15': 'adult_3_15',
    'a3_17': 'adult_3_17',
    'a3_18': 'adult_3_18',
    'a3_19': 'adult_3_19',
    'a3_20': 'adult_3_20',

    'a4_01': 'adult_4_1',
    'a4_02_5b': 'adult_4_2a',
    'a4_03': 'adult_4_3a',
    'a4_04': 'adult_4_4a',
    'a4_05': 'adult_4_5',
    'a4_06': 'adult_4_6',

    'a5_01_9b': 'adult_5_2a',
    'a5_02': 'adult_5_3',
    'a5_03': 'adult_5_4',

    'a6_01': 'adult_6_1',
    'a6_03': 'adult_6_3',
    'a6_03b': 'adult_6_3b',
    'a6_04': 'adult_6_4',
    'a6_05': 'adult_6_5',
    'a6_06_1d': 'adult_6_6d',
    'a6_06_1m': 'adult_6_6c',
    'a6_06_1y': 'adult_6_6b',
    'a6_06_2d': 'adult_6_6h',
    'a6_06_2m': 'adult_6_6g',
    'a6_06_2y': 'adult_6_6f',
    'a6_07d': 'adult_6_7c',
    'a6_07m': 'adult_6_7b',
    'a6_07y': 'adult_6_7a',
    'a6_08': 'adult_6_8',
    'a6_09': 'adult_6_9',
    'a6_10': 'adult_6_10',
    'a6_11': 'adult_6_11',
    'a6_12': 'adult_6_12',
    'a6_13': 'adult_6_13',
    'a6_14': 'adult_6_14',
    'a6_15': 'adult_6_15',

    'c1_01': 'child_1_1',
    'c1_02': 'child_1_2',
    'c1_03': 'child_1_3',
    'c1_04': 'child_1_4',
    'c1_06a': 'child_1_6',
    'c1_06b': 'child_1_6a',
    'c1_07': 'child_1_7',
    'c1_08a': 'child_1_8',
    'c1_08b': 'child_1_8a',
    'c1_11': 'child_1_11',
    'c1_12': 'child_1_12',
    'c1_13': 'child_1_13',
    'c1_14': 'child_1_14',
    'c1_15': 'child_1_15',
    'c1_16': 'child_1_16',
    'c1_17': 'child_1_17',
    'c1_18': 'child_1_18',
    'c1_19_4b': 'child_1_19a',
    'c1_22a': 'child_1_22',
    'c1_22b': 'child_1_22a',
    'c1_23': 'child_1_23',
    'c1_26': 'child_1_26',

    'c2_03': 'child_2_3',
    'c2_04': 'child_2_4',
    'c2_06': 'child_2_6',
    'c2_07': 'child_2_7',
    'c2_08a': 'child_2_8',
    'c2_08b': 'child_2_8a',
    'c2_09': 'child_2_9',
    'c2_11': 'child_2_11',
    'c2_12': 'child_2_12',
    'c2_15a': 'child_2_15',
    'c2_15b': 'child_2_15a',
    'c2_17': 'child_2_17',
    'c2_18': 'child_2_18',

    'c3_01': 'child_3_1',
    'c3_02': 'child_3_2',
    'c3_03_4b': 'child_3_3a',
    'c3_04': 'child_3_4',
    'c3_05': 'child_3_5',
    'c3_06': 'child_3_6',
    'c3_07': 'child_3_7',
    'c3_08': 'child_3_8',
    'c3_09': 'child_3_9',
    'c3_10': 'child_3_10',
    'c3_11': 'child_3_11',
    'c3_12': 'child_3_12',
    'c3_13': 'child_3_13',
    'c3_15': 'child_3_15',
    'c3_16': 'child_3_16',
    'c3_17': 'child_3_17',
    'c3_20': 'child_3_20',
    'c3_23': 'child_3_23',
    'c3_24': 'child_3_24',
    'c3_25': 'child_3_25',
    'c3_26': 'child_3_26',
    'c3_29': 'child_3_29',
    'c3_32': 'child_3_32',
    'c3_33': 'child_3_33',
    'c3_34': 'child_3_34',
    'c3_35': 'child_3_35',
    'c3_36': 'child_3_36',
    'c3_37': 'child_3_37',
    'c3_38': 'child_3_38',
    'c3_39': 'child_3_39',
    'c3_40': 'child_3_40',
    'c3_41': 'child_3_41',
    'c3_42': 'child_3_42',
    'c3_43': 'child_3_43',
    'c3_44': 'child_3_44',
    'c3_45a': 'child_3_45',
    'c3_45b': 'child_3_45a',
    'c3_46': 'child_3_46',
    'c3_47': 'child_3_47',
    'c3_48': 'child_3_48',
    'c3_49': 'child_3_49',

    'c4_01': 'child_4_1',
    'c4_03': 'child_4_3',
    'c4_04': 'child_4_4',
    'c4_05': 'child_4_5',
    'c4_06': 'child_4_6',
    'c4_07a': 'child_4_7',
    'c4_07b': 'child_4_7a',
    'c4_09': 'child_4_9',
    'c4_11': 'child_4_11',
    'c4_12': 'child_4_12',
    'c4_14': 'child_4_14',
    'c4_15': 'child_4_15',
    'c4_16': 'child_4_16',
    'c4_18': 'child_4_18',
    'c4_20': 'child_4_20',
    'c4_22': 'child_4_22',
    'c4_23': 'child_4_23',
    'c4_24': 'child_4_24',
    'c4_25': 'child_4_25',
    'c4_26': 'child_4_26',
    'c4_27': 'child_4_27',
    'c4_28': 'child_4_28',
    'c4_29': 'child_4_29',
    'c4_30': 'child_4_30',
    'c4_31_1': 'child_4_31',
    'c4_32': 'child_4_32',
    'c4_34': 'child_4_34',
    'c4_35': 'child_4_35',
    'c4_36': 'child_4_36',
    'c4_38': 'child_4_38',
    'c4_39': 'child_4_39',
    'c4_40': 'child_4_40',
    'c4_41': 'child_4_41',
    'c4_42': 'child_4_42',
    'c4_43': 'child_4_43',
    'c4_44': 'child_4_44',
    'c4_45': 'child_4_45',
    'c4_46': 'child_4_46',
    'c4_47_8b': 'child_4_48a',

    'c5_01': 'child_5_1',
    'c5_03': 'child_5_3',
    'c5_04': 'child_5_4',
    'c5_05': 'child_5_5',
    'c5_06_1d': 'child_5_6d',
    'c5_06_1m': 'child_5_6c',
    'c5_06_1y': 'child_5_6b',
    'c5_06_2d': 'child_5_7d',
    'c5_06_2m': 'child_5_7c',
    'c5_06_2y': 'child_5_7b',
    'c5_07_1a': 'child_5_6e',
    'c5_07_1b': 'child_5_6f',
    'c5_07_2a': 'child_5_7e',
    'c5_07_2b': 'child_5_7f',
    'c5_08d': 'child_5_8c',
    'c5_08m': 'child_5_8b',
    'c5_08y': 'child_5_8a',
    'c5_09': 'child_5_9',
    'c5_10': 'child_5_10',
    'c5_11': 'child_5_11',
    'c5_12': 'child_5_12',
    'c5_13': 'child_5_13',
    'c5_14': 'child_5_14',
    'c5_15': 'child_5_15',
    'c5_16': 'child_5_16',
    'c5_17': 'child_5_17',
    'c5_18': 'child_5_18',
    'c5_19': 'child_5_19',
}

"""(GHDx column) -> (ODK unit column, ODK value column, unit)"""
DURATION_VARS = {
    'a2_01': ('adult_2_1', 'adult_2_1c', 4),
    'a2_03': ('adult_2_3', 'adult_2_3a', 4),
    'a2_08': ('adult_2_8', 'adult_2_8a', 4),
    'a2_15': ('adult_2_15', 'adult_2_15a', 4),
    'a2_22': ('adult_2_22', 'adult_2_22a', 4),
    'a2_24': ('adult_2_24', 'adult_2_24a', 4),
    'a2_26': ('adult_2_26', 'adult_2_26a', 4),
    'a2_28': ('adult_2_28', 'adult_2_28a', 4),
    'a2_33': ('adult_2_33', 'adult_2_33a', 4),
    'a2_37': ('adult_2_37', 'adult_2_37a', 4),
    'a2_41': ('adult_2_41', 'adult_2_41a', 4),
    'a2_48': ('adult_2_48', 'adult_2_48a', 4),
    'a2_54': ('adult_2_54', 'adult_2_54b', 4),
    'a2_58': ('adult_2_58', 'adult_2_58a', 4),
    'a2_62': ('adult_2_62', 'adult_2_62b', 4),
    'a2_65': ('adult_2_65', 'adult_2_65a', 4),
    'a2_68': ('adult_2_68', 'adult_2_68a', 4),
    'a2_70': ('adult_2_70', 'adult_2_70b', 4),
    'a2_73': ('adult_2_73', 'adult_2_73a', 4),
    'a2_76': ('adult_2_76', 'adult_2_76a', 4),
    'a2_79': ('adult_2_79', 'adult_2_79a', 4),
    'a2_83': ('adult_2_83', 'adult_2_83b', 5),   # hours
    'a2_86': ('adult_2_86', 'adult_2_86a', 4),
    'a3_08': ('adult_3_8', 'adult_3_8a', 3),   # weeks
    'a3_11': ('adult_3_11', 'adult_3_11a', 2),   # months
    'a3_16': ('adult_3_16', 'adult_3_16a', 5),   # hours

    'a5_04': ('adult_5_5', 'adult_5_5b', 4),
    'c1_05': ('child_1_5', 'child_1_5a', 4),
    'c1_20': ('child_1_20', 'child_1_20a', 4),
    'c1_21': ('child_1_21', 'child_1_21a', 4),
    'c1_25': ('child_1_25', 'child_1_25a', 4),
    'c2_02': ('child_2_2', 'child_2_2a', 2),   # months
    'c2_05': ('child_2_5', 'child_2_5', 4),
    'c2_10': ('child_2_10', 'child_2_10a', 5),   # hours
    'c3_14': ('child_3_14', 'child_3_14a', 4),
    'c3_18': ('child_3_18', 'child_3_18a', 4),
    'c3_19': ('child_3_19', 'child_3_19a', 4),
    'c3_21': ('child_3_21', 'child_3_21a', 4),
    'c3_22': ('child_3_22', 'child_3_22a', 4),
    'c3_27': ('child_3_27', 'child_3_27a', 4),
    'c3_28': ('child_3_28', 'child_3_28a', 4),
    'c3_30': ('child_3_30', 'child_3_30a', 4),
    'c3_31': ('child_3_31', 'child_3_31a', 4),
    'c4_02': ('child_4_2', 'child_4_2a', 4),
    'c4_08': ('child_4_8', 'child_4_8a', 4),
    'c4_10': ('child_4_10', 'child_4_10a', 4),
    'c4_13': ('child_4_13', 'child_4_13a', 4),
    'c4_17': ('child_4_17', 'child_4_17a', 4),
    'c4_19': ('child_4_19', 'child_4_19a', 4),
    'c4_33': ('child_4_33', 'child_4_33a', 4),
    'c4_37': ('child_4_37', 'child_4_37a', 4),
    'c4_49': ('child_4_50', 'child_4_50b', 4),
}

"""(ODK column) -> ([GHDx columns], [missing values])"""
MULTISELECT_CATEGORICAL_VARS = {
    'adult_2_9': (['a2_09_1a', 'a2_09_2a'], [8, 9]),   # Rash
    'adult_2_39': (['a2_39_1', 'a2_39_2'], [8, 9]),   # Breathing position
}

"""(ODK column) -> {(GHDx column) -> (ODK value)}"""
MULTISELECT_BINARY_VARS = {
    'adult_2_87': {   # paralysis
        'a2_87_1': 1,
        'a2_87_2': 2,
        'a2_87_3': 3,
        'a2_87_4': 4,
        'a2_87_5': 5,
        'a2_87_6': 6,
        'a2_87_7': 7,
        'a2_87_8': 8,
        'a2_87_9': 9,
        'a2_87_10a': 11,
    },
    'adult_4_2': {   # tobacco
        'a4_02_1': 1,
        'a4_02_2': 2,
        'a4_02_3': 3,
        'a4_02_4': 4,
        'a4_02_5a': 11,
        'a4_02_6': 8,
        'a4_02_7': 9,
    },
    'adult_5_2': {   # injuries
        'a5_01_1': 1,
        'a5_01_2': 2,
        'a5_01_3': 3,
        'a5_01_4': 4,
        'a5_01_5': 5,
        'a5_01_6': 6,
        'a5_01_7': 7,
        'a5_01_9a': 11,
    },
    'adult_6_2': {   # seek care
        'a6_02_1': 1,
        'a6_02_2': 2,
        'a6_02_3': 3,
        'a6_02_4': 4,
        'a6_02_5': 5,
        'a6_02_6': 6,
        'a6_02_7': '',   # no endorsements or ODK value...
        'a6_02_8': 7,
        'a6_02_9': 8,
        'a6_02_10': 9,
        'a6_02_11': 10,
        'a6_02_12a': 11,
        'a6_02_13': 12,
        'a6_02_14': 88,
        'a6_02_15': 99,
    },
    'child_1_19': {   # abnormalities
        'c1_19_1': 1,
        'c1_19_2': 2,
        'c1_19_3': 3,
        'c1_19_4a': 11,
        'c1_19_5': 8,
    },
    'child_2_1': {   # complications
        'c2_01_1': 1,
        'c2_01_2': 2,
        'c2_01_3': 3,
        'c2_01_4': 4,
        'c2_01_5': 5,
        'c2_01_6': 6,
        'c2_01_7': 7,
        'c2_01_8': 8,
        'c2_01_9': 9,
        'c2_01_10': 10,
        'c2_01_11': 88,
        'c2_01_12': 99,
    },
    'child_3_3': {   # abnormalities
        'c3_03_1': 1,
        'c3_03_2': 2,
        'c3_03_3': 3,
        'c3_03_4a': 11,
        'c3_03_5': 8,
        'c3_03_6': 9,
    },
    'child_4_48': {   # injuries
        'c4_47_1': 1,
        'c4_47_2': 2,
        'c4_47_3': 3,
        'c4_47_4': 4,
        'c4_47_5': 5,
        'c4_47_6': 6,
        'c4_47_7': 7,
        'c4_47_8a': 11,
        'c4_47_9': 9,
        'c4_47_10': 8,
    },
    'child_5_2': {   # seek care
        'c5_02_1': 1,
        'c5_02_2': 2,
        'c5_02_3': 3,
        'c5_02_4': 4,
        'c5_02_5': 5,
        'c5_02_6': 6,
        'c5_02_7': 7,
        'c5_02_8': 8,
        'c5_02_9': 9,
        'c5_02_10': 10,
        'c5_02_11a': 11,
        'c5_02_12': 12,
        'c5_02_13': 88,
        'c5_02_14': 99,
    }
}

"""(module string) -> (ODK column)"""
FREETEXT_VARS = {
    'adult': 'adult_7_c',
    'child': 'child_6_c',
    'neonate': 'neonate_6_c'
}


if __name__ == '__main__':
    main()
