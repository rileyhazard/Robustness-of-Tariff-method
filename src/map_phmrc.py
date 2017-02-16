import os

import numpy as np
import pandas as pd

from data.map_ghdx_data import *
from mapping import *
from getters import get_codebook
from download_ghdx import (
    download_ghdx_data,
    load_local_ghdx_data,
    GHDX_CODEBOOK,
    GHDX_FILENAME,
    MODULES,
)


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

    # The word 'pox' was mistranslated in the original survey. The intended
    # meaning is 'rash'. Correct the free text as suggested by Ian Riley.
    df.word_rash = df.word_rash + df.word_pox
    df.drop('word_rash', axis=1, inplace=True)

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
    full.loc[:, odk_codebook.loc[odk_codebook.full == 0].index] = ''
    full.to_csv(os.path.join(outdir, 'odk', 'phmrc_full.csv'), index=False)

    short = df.copy()
    short.loc[:, odk_codebook.loc[odk_codebook.short == 0].index] = ''
    short.to_csv(os.path.join(outdir, 'odk', 'phmrc_short.csv'), index=False)

    return df


if __name__ == '__main__':
    main()
