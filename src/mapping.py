import re
import os

import numpy as np
import pandas as pd


"""(module string) -> (ODK column)"""
ODK_LONG_FREETEXT_VARS = {
    'adult': 'adult_7_c',
    'child': 'child_6_c',
    'neonate': 'neonate_6_c'
}

"""(ODK short form variable) -> (all required symptom variable)"""
ODK_FREETEXT_SHORT_TO_LONG = {
    'adult_7_1': ['chronic', 'kidney'],
    'adult_7_2': ['dialysi'],
    'adult_7_3': ['fever'],
    'adult_7_4': ['ami'],
    'adult_7_5': ['heart'],
    'adult_7_6': ['jaundic'],   # not yellow or skin
    'adult_7_7': ['liver', 'failur'],
    'adult_7_8': ['malaria'],
    'adult_7_9': ['pneumonia'],
    'adult_7_10': ['renal', 'failur'],   # not kidney
    'adult_7_11': ['suicid'],
    'child_6_1': ['abdomen'],
    'child_6_2': ['cancer'],
    'child_6_3': ['dehydr'],
    'child_6_4': ['dengu'],   # not fever
    'child_6_5': ['diarrhea'],
    'child_6_6': ['fever'],
    'child_6_7': ['heart'],
    'child_6_8': ['jaundic'],   # not yellow or skin
    'child_6_9': ['pneumonia'],
    'child_6_10': ['rash'],
    'neonate_6_1': ['asphyxia'],
    'neonate_6_2': ['incub'],
    'neonate_6_3': ['lung'],
    'neonate_6_4': ['pneumonia'],
    'neonate_6_5': ['preterm'],
    'neonate_6_6': ['respiratori', 'distress'],
}


def combine_freetext(series):
    """Create a string to use as freetext from a series of word frequencies"""
    words_cols = series.loc[series > 0].index
    if words_cols.any():
        return ' '.join(words_cols.str.lstrip('word_'))
    return ''


def concat_str(series):
    return ' '.join(series.replace('', np.nan).dropna().astype(str))


def concat_encoded(series, missing=None):
    """Concatenate nomissing values as a string of integers"""
    series = series.dropna().drop_duplicates().astype(int).astype(str)
    if len(series) == 1:
        return series.iloc[0]
    if missing:
        series = series.replace(missing, np.nan)
    return ' '.join(series)


def concat_binary(series, mapping):
    """Concatentate values of binarized symptoms as a string of integers"""
    endorsed = pd.Series(mapping).loc[series == 1]
    return ' '.join(endorsed.astype(int).astype(str))


def infer_dtype(x):
    """Cast to int or float if possible"""
    try:
        float_ = float(x)
    except ValueError:
        float_ = None
    try:
        int_ = int(float(x))
    except ValueError:
        int_ = None
    if not float_ and not int_:
        return x
    else:
        if int_ == float_:
            return int_
        else:
            return float_


def lookup_default(coding_str):
    """Find the encoded value to use as a default if no data is given"""
    mapping = mapping_from_coding(coding_str)
    if mapping:
        for key in ["Don't Know", "Unknown"]:
            if key in mapping:
                return int(mapping[key])
    return np.nan


def mapping_from_coding(coding_str):
    """Return a dict to map from codebook string to integer"""
    if isinstance(coding_str, basestring):
        return dict(zip(re.findall('(?<= ").+?(?=")', coding_str),
                        map(int, re.findall('\d+(?= ")', coding_str))))


def calc_agedays(series, vars):
    """Calculate age days from a series ODK age columns"""
    years, months, days = series.loc[vars].fillna(0)
    return years * 365 + months * 30 + days


def calc_agegroup(series, vars):
    """Calculate ODK agegroup from ODK age numeric columns"""
    # If nothing is listed use the agegroup listed in the file title
    age_groups = {'Adult': 3, 'Child': 2, 'Neonate': 1, 'Stillbirth': 0}
    if series[vars].isnull().all():
        return age_groups[series.module]

    agedays = calc_agedays(series, vars)
    if agedays == 0:
        return 0
    if 0 < agedays < 28:
        return 1
    if 28 <= agedays < 12 * 365:
        return 2
    if agedays >= 12 * 365:
        return 3


def get_codebook(form):
    """Get the codebook for a specified format"""
    filepath = os.path.abspath(os.path.dirname(__file__))
    cb_path = os.path.join(filepath, '..', 'codebooks', '{}.csv'.format(form))
    return pd.read_csv(cb_path, index_col=0)


def get_short_drop(form):
    """Get the list of columns to drop for the short form question"""
    cb = get_codebook(form)
    return cb.loc[cb.long_only != 1].index.tolist()
