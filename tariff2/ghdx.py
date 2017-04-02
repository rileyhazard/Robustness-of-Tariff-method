import os
import warnings

import pandas as pd

from tariff2 import MODULES, REPO_DIR
from tariff2.data.map_ghdx_data import *
from tariff2.loaders import get_codebook


GHDX_CODEBOOK = 'IHME_PHMRC_VA_DATA_CODEBOOK_Y2013M09D11_0.csv'
GHDX_FILENAME = 'IHME_PHMRC_VA_DATA_{}_Y2013M09D11_{}.csv'
GHDX_DIR = os.path.join(REPO_DIR, 'data', 'ghdx')


def load_ghdx_data(module):
    """Load GHDx PHMRC files from the repo"""
    i = 2 if module == 'child' else 1
    filename = GHDX_FILENAME.format(module.upper(), i)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', pd.io.common.DtypeWarning)
        df = pd.read_csv(os.path.join(GHDX_DIR, filename))
    df['sid'] = df.module + df.newid.astype(int).astype(str)
    return df.set_index('sid')


def save_ghdx_gold_standards():
    gs_cols = ['site', 'module', 'gs_text46', 'gs_text34', 'gs_level']
    outfile = os.path.join(REPO_DIR, 'data', 'gold_standards', 'ghdx_gs.csv')

    df = pd.concat([load_ghdx_data(module)[gs_cols] for module in MODULES])

    # Nobody cares about the 11 neonate causes, only the 6, so replace it
    neonate = df.module == 'Neonate'
    df.loc[neonate, 'gs_text46'] = df.loc[neonate, 'gs_text34']
    df.drop('gs_text34', axis=1).to_csv(outfile)


def clean_ghdx_codebook():
    """Clean the codebock and add information about column type"""
    df = pd.read_csv(os.path.join(GHDX_DIR, GHDX_CODEBOOK), index_col=0)

    df.loc[df.coding.notnull(), 'type'] = 'categorical'
    df.loc[df.coding.isnull(), 'type'] = 'numeric'
    df.loc[df.index.str.startswith('word_'), 'type'] = 'word'
    df.loc[['site', 'g2_01', 'g2_02'], 'type'] = 'info'

    # Some numeric variables have a sentinel value for missing which appears
    # in the coding coding. This value is always a set of 9s as "Don't Know"
    # Since this is the only coding it appears at the begining of the string
    num_with_dk = df.coding.str.contains('^9+ "Don\'t Know"').fillna(False)
    df.loc[num_with_dk, 'type'] = 'numeric'

    # These regexs are designned to NOT match the string '[specify unit]',
    # which is a numeric encoding of the unit
    freetext_re = 'specified|, specify|from the certificate|Record from where'
    df.loc[df.question.str.contains(freetext_re), 'type'] = 'freetext'

    # This columns is not actually in the data
    df.drop('gs_diagnosis', inplace=True)

    # The codebook is missing a space between the 1 and "Grams" which causes
    # the mapping from coding function to fail
    df.loc['c1_08a', 'coding'] = ('1 "Grams" 8 "Refused to Answer" '
                                  '9 "Don\'t Know"')

    # The codebook does not mention that the values 9999 is used as a sentinel
    # for missing for child weight at previous medical visits
    df.loc[['c5_07_1', 'c5_07_2'], 'coding'] = '9999 "Don\'t Know"'

    df.to_csv(os.path.join(REPO_DIR, 'codebooks', 'ghdx.csv'))
    return df


def load_fixed_ghdx_data(module):
    """Load GHDx PHMRC files from the repo and apply various data fixes.

    Args:
        module (str): 'adult', 'child', or 'neonate'

    Returns:
        (dataframe): fixed GHDx data

    See Also:
        fix_ghdx_ages
        fix_ghdx_pox
        fix_ghdx_injuries
        fix_ghdx_birth_weight
    """
    df = load_ghdx_data(module)
    df = fix_ghdx_ages(df)
    df = fix_ghdx_pox(df)
    df = fix_ghdx_injuries(df)
    df = fix_ghdx_birth_weights(df)
    return df


def fix_ghdx_ages(df):
    """Fix inconsistency in the age variables.

    Some entries of age variables are very obvious transcription errors. These
    lead to misclassifying an observation into the wrong age-specific module.

    Args:
        df (dataframe): GHDx data.

    Returns:
        (dataframe): the same dataframe is returned with inplace modifications.
    """
    idx = df.index.intersection(['Adult3138', 'Adult7459'])
    df.loc[idx, 'g5_04a'] = df.loc[idx, 'g5_04c']
    df.loc[idx, 'g5_04c'] = float('nan')

    idx = df.index.intersection(['Child954', 'Child1301', 'Child1329'])
    df.loc[idx, 'g5_04b'] = df.loc[idx, 'g5_04a']
    df.loc[idx, 'g5_04a'] = float('nan')

    idx = df.index.intersection(['Child1372'])
    df.loc[idx, 'g5_04c'] = 29

    idx = df.index.intersection(['Child2062'])
    df.drop(idx, inplace=True)

    idx = df.index.intersection(['Neonate545', 'Neonate2152'])
    df.loc[idx, 'g5_04c'] = df.loc[idx, 'g5_04a']
    df.loc[idx, 'g5_04a'] = float('nan')

    idx = df.index.intersection(['Neonate1192', 'Neonate1377'])
    df.loc[idx, 'g5_04c'] = df.loc[idx, 'g5_04b']
    df.loc[idx, 'g5_04b'] = float('nan')

    return df


def fix_ghdx_pox(df):
    """Fix the word pox by recoding it to rash.

    The version of the survey instrument fielded in Udar Pradesh clearly
    mistranslated the word pox to something very close to the rash. At other
    sites the translations of the word pox and rash were not adequate to
    distinguish the two words. The GHDx child data contains 15 endorsements
    for the word pox, 13 for Udar Pradesh and 2 from Bohol. These should all
    be recoded to the word rash.

    Args:
        df (dataframe): GHDx data.

    Returns:
        (dataframe): the same dataframe is returned with inplace modifications.
    """
    if 'word_pox' in df:
        df.word_rash = df.word_rash + df.word_pox
        df.drop('word_pox', axis=1, inplace=True)
    return df


def fix_ghdx_injuries(df):
    """Remove injury endorsement which occured more than 30 days before death.

    The original survey instrument asked the question about injuries in a very
    open ended manner which was interpreted as any injuries ever, as opposed
    to the injuries leading to death. The subsequent analysis dropped injuries
    which occured more than 30 days before death.

    Args:
        df (dataframe): GHDx data.

    Returns:
        (dataframe): the same dataframe is returned with inplace modifications.
    """
    if 'a5_04' in df:
        mask = df.a5_04 > 30
        for col in df.filter(like='a5_').columns:
            df.loc[mask & df[col].notnull(), col] = 0
    if 'c4_49' in df:
        mask = df.c4_49 > 30
        for col in df.filter(regex='c4_47_|c4_48|c4_49').columns:
            df.loc[mask & df[col].notnull(), col] = 0
    return df


def fix_ghdx_birth_weights(df):
    """Ensure the child birth weight is in grams and is a legal value.

    The original survey allowed answers to weights to be coded in grams or
    kilograms. The GHDx data has recoded the values into grams. However, a
    few cases are clearly still coded in kilograms. The survey also used the
    value 9999 as a sentinel for missing weight in grams. The updated survey
    instrument allows child birth weights between 0.5 kg and 8 kg. We will
    use this as the valid range.

    Args:
        df (dataframe): GHDx data.

    Returns:
        (dataframe): the same dataframe is returned with inplace modifications.
    """
    if 'c1_08b' in df:
        df.loc[df.c1_08b <= 8, 'c1_08b'] = df.c1_08b * 1000   # g => kg
        df.loc[(df.c1_08b > 8) & (df.c1_08b < 500), 'c1_08b'] = float('nan')
    return df


def concat_str(series):
    return ' '.join(series.dropna().map(str))


def combine_freetext(series):
    """Create a string to use as freetext from a series of word frequencies"""
    return ' '.join([col[5:] for col in series.loc[series > 0].index])


def concat_encoded(series, missing=None):
    """Concatenate nomissing values as a string of integers"""
    if missing:
        series = series.replace(missing, float('nan'))
    series = series.dropna().drop_duplicates().map(int).map(str)
    return series.iloc[0] if len(series) == 1 else ' '.join(series)


def concat_binary(series, mapping):
    """Concatentate values of binarized symptoms as a string of integers"""
    endorsed = pd.Series(mapping).loc[series == 1]
    return ' '.join(endorsed.map(int).map(str))


def calc_agedays(series, age_vars):
    """Calculate age days from a series ODK age columns"""
    years, months, days = series.loc[age_vars].fillna(0)
    return years * 365 + months * 30 + days


def calc_agegroup(series, age_vars):
    """Calculate ODK agegroup from ODK age numeric columns"""
    # If nothing is listed use the agegroup listed in the file title
    age_groups = {'Adult': 3, 'Child': 2, 'Neonate': 1, 'Stillbirth': 0}
    if series[age_vars].isnull().all():
        return age_groups[series.module]

    agedays = calc_agedays(series, age_vars)
    if agedays == 0:
        return 0
    if 0 < agedays < 28:
        return 1
    if 28 <= agedays < 12 * 365:
        return 2
    if agedays >= 12 * 365:
        return 3


def map_ghdx_to_odk(codebook):
    """
    """
    df = pd.concat([load_fixed_ghdx_data(module) for module in MODULES])

    # Some numeric columns contain a sentinel value for missing which was
    # encoded as some number of nines. These should be removed so they are
    # not confused for real durations
    cb = codebook.loc[(codebook.type == 'numeric') & codebook.coding.notnull()]
    numerics = cb.coding.str.rstrip(' "Don\'t Know"').astype(int)
    for col, missing in numerics.iteritems():
        if col in df:
            df.loc[df[col] == missing, col] = float('nan')

    # ODK only has a single "select one" question for location of belly pain.
    # Upper belly pain is not relevant for tariff, only lower belly pain is
    # important. If lower belly pain is in the secondary belly pain location
    # it should be moved to the variable which is mappped to the ODK variable.
    if 'a2_63_1' in df and 'a2_63_2' in df:
        df.loc[df.a2_63_2 == 2, 'a2_63_1'] = 2

    # Create the injury screening questions. The dataset has an indicator
    # for "Experienced no injuries". If this is endorsed than the injury
    # screening question should not be endorsed
    if 'a5_01_8' in df:
        df['adult_5_1'] = df.a5_01_8.map(lambda x: int(x != 1))
    if 'c4_47_11' in df:
        df['child_4_47'] = df.c4_47_11.map(lambda x: int(x != 1))

    # The PHMRC dataset has two variables for "other specified" rash location
    # for adults. These should be combined into a single string in the first
    # column which is mapped to the ODK variable
    if 'a2_09_1b' in df and 'a2_09_2b' in df:
        df.a2_09_1b = df[['a2_09_1b', 'a2_09_2b']].apply(concat_str, axis=1)

    # Duration variables in the data files are in a single variable and have
    # been converted to days. ODK is expecting a variable which says the unit
    # a variable with the value in that unit.
    duration_scalar = {2: 1 / 30, 3: 1 / 7, 4: 1, 5: 24}
    for orig_col, (unit_col, val_col, unit_val) in DURATION_VARS.items():
        if orig_col in df:
            df[unit_col] = unit_val
            df[val_col] = df[orig_col] * duration_scalar[unit_val]

    # ODK encodes multiselect answers as strings of space separated ints
    # The datasets split multiselects into series of columns. There are two
    # formats: 1) multiple encoded categoricals and 2) binarized
    for target, (sources, missing) in MULTISELECT_CATEGORICAL_VARS.items():
        if df.columns.intersection(sources).any():
            df[target] = df[sources].apply(concat_encoded, missing=missing,
                                           axis=1)
    for target, mapping in MULTISELECT_BINARY_VARS.items():
        cols = df.columns.intersection(mapping.keys())
        if cols.any():
            df[target] = df[cols].apply(concat_binary, mapping=mapping, axis=1)

    # Multiselect dates (a6_06, c5_06) not used in Smartva...

    # Map the column names to ODK
    df = df.rename(columns=VAR_CONVERSION_MAP)

    # Create age variables from ODK ages columns
    df['agedays'] = df.apply(calc_agedays, age_vars=ODK_AGE_VARS, axis=1)
    df['gen_5_4d'] = df.apply(calc_agegroup, age_vars=ODK_AGE_VARS, axis=1)

    # Combine words into dummy freetext
    freetext = df.filter(like="word_").apply(combine_freetext, axis=1)
    for module, var in FREETEXT_VARS.items():
        df.loc[df.module.str.lower() == module, var] = freetext

    # Map to the short form freetext variables
    for short, full in ODK_FREETEXT_SHORT_TO_LONG.items():
        cols = df.columns.intersection(['word_{}'.format(w) for w in full])
        if cols.any():
            df[short] = df.loc[:, cols].all(1).map(int)
        else:
            df[short] = 0

    return df


def remove_float_zero(x):
    """Remove the trailing ".0" from stringifying floats"""
    return x[:-2] if x.endswith('.0') else x


def main():
    save_ghdx_gold_standards()
    codebook = clean_ghdx_codebook()
    df = map_ghdx_to_odk(codebook)
    df = df.fillna('').astype(str).applymap(remove_float_zero)

    odk_codebook = get_codebook('odk').drop('sid')
    df = df.loc[:, odk_codebook.index.tolist()].fillna('')

    full = df.copy()
    full.loc[:, odk_codebook.loc[odk_codebook.full == 0].index] = ''
    full.to_csv(os.path.join(REPO_DIR, 'data', 'odk', 'ghdx_full.csv'))

    short = df.copy()
    short.loc[:, odk_codebook.loc[odk_codebook.short == 0].index] = ''
    short.to_csv(os.path.join(REPO_DIR, 'data', 'odk', 'ghdx_short.csv'))


if __name__ == '__main__':
    main()
