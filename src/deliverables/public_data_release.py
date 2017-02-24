import os
import re

import pandas as pd
import numpy as np
from stemming.porter2 import stem

from getters import (
    REPO_DIR,
    get_gold_standard,
    get_cause_map,
    get_codebook,
)

ODK_FREETEXT_COLS = ['adult_7_c', 'child_6_c', 'neonate_6_c']


def remove_pid(df, dates=None, ages=None, freetext=None, other=None,
               words=None, replaces=None):
    """Remove personally identifying information from the survey data

    Args:
        df (dataframe): raw data
        dates (list or str): columns labels of date variables to drop
        ages (list or str): column labels of age variables in years
        freetext (list of str): column labels of freetext variables
        freetext_name (str): name of the column which will contain all
            relevant freetext
        replaces (dict): mapping of word replacements

    Returns:
        (dataframe)
    """
    df = df.copy()

    # Drop personally identifying dates (birth dates, date of death, etc.)
    if dates:
        df.loc[:, df.columns.intersection(dates)] = np.nan

    # Truncate ages at 80 for privacy
    if ages:
        ages = df.columns.intersection(ages)
        df.loc[:, ages] = df[ages].applymap(lambda x: 80 if x > 80 else x)
        # todo: handle agedays

    # Only keep important words as a single freetext variable
    if freetext:
        freetext_cols = df.columns.intersection(freetext)
        with_text = []
        for module in ['adult', 'child', 'neonate']:
            mod = df.loc[df.module == module, freetext_cols]
            mod = mod.apply(collect_freetext, axis=1, words=words[module],
                            replaces=replaces)
            with_text.append(mod)
        with_text.insert(0, df)
        df = pd.concat(with_text, axis=1)
        df.index.name = 'sid'
        df.loc[:, freetext_cols] = np.nan
        df = df.rename(columns=dict(zip(range(3), ODK_FREETEXT_COLS)))

    if other:
        df.loc[:, df.columns.intersection(other)] = np.nan

    return df


def collect_freetext(series, words=None, replaces=None):
    """Concatenate all the freetext into a single series keeping only words

    Args:
        series (series): data with only freetext columns
        words (list?): strings of tokens to keep

    Returns:
        (series)
    """
    if words is None:
        return np.nan

    text = ' '.join(series.dropna().astype(str))
    if not text.split():   # only white space
        return np.nan

    text = re.sub('[^a-z ]', '', ' '.join(text.split()).lower())

    if replaces:
        for src, target in replaces.items():
            text = re.sub(' {} '.format(src), ' {} '.format(target), text)

    text = [word for word in text.split() if stem(word) in words]
    np.random.shuffle(text)   # for fun... and privacy

    return ' '.join(text)


def add_gold_standards(df, dataset, cause_map):
    """
    """
    if dataset not in ['phmrc', 'nhmrc']:
        raise ValueError('Unknown dataset: "{}"'.format(dataset))

    gs = get_gold_standard(dataset)

    def recode_gs(row):
        return cause_map[row.get('module')][row.get('gs_text46')]

    cols = df.columns.tolist()
    df['module'] = gs.module
    df['gs_analytic'] = gs.gs_text46
    df['gs_reporting'] = gs.apply(recode_gs, axis=1)

    cols = ['module', 'gs_analytic', 'gs_reporting'] + cols
    df = df.loc[df.module.notnull() & df.gs_analytic.notnull(), cols]

    return df


def get_words_by_module(module):
    """
    """
    cb = get_codebook('{}_symptom.csv'.format(module))
    words = cb.loc[cb.index.str.startswith('s9999'), 'question']
    words = words.str.slice(5)   # remove 'word_'
    return words.tolist()


def main():
    modules = ['adult', 'child', 'neonate']
    cause_map = {module: get_cause_map(module, 'smartva_text', 'gs_text34')
                 for module in modules}
    words = {module: get_words_by_module(module) for module in modules}
    cb = get_codebook('odk')

    ages = ['gen_5_4a']
    dates = ['gen_5_1a', 'gen_5_1b', 'gen_5_lc',
             'gen_5_3a', 'gen_5_3b', 'gen_5_3c',
             'adult_6_6b', 'adult_6_6c', 'adult_6_6d',
             'adult_6_6f', 'adult_6_6g', 'adult_6_6h',
             'adult_6_7a', 'adult_6_7b', 'adult_6_7c',
             'child_5_6b', 'child_5_6c', 'child_5_6d',
             'child_5_7b', 'child_5_7c', 'child_5_7d',
             'child_5_8a', 'child_5_8b', 'child_5_8c',
             ]
    freetext = cb.loc[cb.type == 'text'].index.tolist()
    pid = cb.loc[cb.type == 'info'].index.tolist()

    for instr in ['short', 'full']:
        for dataset in ['phmrc', 'nhmrc']:
            filename = '{}_{}.csv'.format(dataset, instr)
            infile = os.path.join(REPO_DIR, 'data', 'odk', filename)
            df = pd.read_csv(infile).set_index('sid')
            df = add_gold_standards(df, dataset, cause_map)
            df = remove_pid(df, dates, ages, freetext, pid,
                            words=words, replaces=WORD_SUBS)
            if instr == 'short':
                df.loc[:, ODK_FREETEXT_COLS] = np.nan
            if 'phmrc':
                col_order = df.columns.tolist()
            else:
                df['counter'] = range(df.shape[0])
                df.index = df.counter.map(lambda x: 'NHMRC{}'.format(x))
                df.drop('counter', axis=1, inplace=True)
                df = df.loc[:, col_order]

            df.to_csv(os.path.join(REPO_DIR, 'external', 'data_release',
                                   filename))


WORD_SUBS = {
    'abdomin': 'abdomen',
    'abdominal': 'abdomen',
    'accidentally': 'accident',
    'accidental': 'accident',
    'accidently': 'accident',
    'acute myocardial infarction': 'ami',
    'aids': 'hiv',
    'anaemia': 'anemia',
    'anemic': 'anemia',
    'baby\'s': 'babi',
    'babies': 'babi',
    'baby': 'babi',
    'bit': 'bite',
    'bitten': 'bite',
    'bleed': 'blood',
    'bleeding': 'blood',
    'blood pressure': 'hypertension',
    'burn': 'fire',
    'burns': 'fire',
    'burnt': 'fire',
    'burned': 'fire',
    'burning': 'fire',
    'burnings': 'fire',
    'c section': 'csection',
    'caesarean': 'cesarean',
    'caesarian': 'cesarean',
    'cancerous': 'cancer',
    'carcinoma': 'cancer',
    'cardiac': 'cardio',
    'cardiogenic': 'cardio',
    'cerebrovascular': 'cerebral',
    'cervical': 'cervix',
    'cesarian': 'cesarean',
    'comatose': 'coma',
    'convulsions': 'convulsion',
    'death': 'dead',
    'dehydrated': 'dehydrate',
    'dehydration': 'dehydrate',
    'delivered': 'deliver',
    'deliveries': 'deliver',
    'delivery': 'deliver',
    'diarrheal': 'diarrhea',
    'difficult breath': 'dyspnea',
    'difficult breathing': 'dyspnea',
    'difficulty ': 'difficult',
    'digestion': 'digest',
    'digestive': 'digest',
    'dog bite': 'dogbite',
    'drank': 'drink',
    'drawn': 'drown',
    'drowned': 'drown',
    'drowning': 'drown',
    'drunk': 'drink',
    'dysentary': 'diarrhea',
    'dyspneic': 'dyspnea',
    'eclaupsia': 'eclampsia',
    'edemata': 'edema',
    'edematous': 'edema',
    'edoema': 'edema',
    'ekg': 'ecg',
    'esophageal': 'esophag',
    'esophagus': 'esophag',
    'fallen': 'fall',
    'falling': 'fall',
    'feet': 'foot',
    'fell': 'fall',
    'heart attack': 'ami',
    'herniation': 'hernia',
    'hypertensive': 'hypertension',
    'incubator': 'incubate',
    'infected': 'infect',
    'infectious': 'infect',
    'injured': 'injury',
    'injures': 'injury',
    'injuries': 'injury',
    'ischemic': 'ischemia',
    'labour': 'labor',
    'maternity': 'maternal',
    'msb': 'stillbirth',
    'oxygenated': 'oxygen',
    'paralysis': 'paralyze',
    'pnuemonia': 'pneumonia',
    'poisoning': 'poison',
    'poisonous': 'poison',
    'pregnant': 'pregnancy',
    'premature': 'preterm',
    'prematurity': 'preterm',
    'septic': 'sepsis',
    'septicaemia': 'sepsis',
    'septicemia': 'sepsis',
    'smoker': 'smoke',
    'stroked': 'stroke',
    'swollen': 'swell',
    'tb': 'tb',
    't.b': 'tb',
    't.b.': 'tb',
    'transfussed': 'transfuse',
    'transfussion': 'transfuse',
    'tuberculosis': 'tb',
    'urinary': 'urine',
    'venomous': 'venom',
    'violent': 'violence',
    'vomits': 'vomit',
    'vomitting': 'vomit',
    'yellowish': 'yellow'
}

if __name__ == '__main__':
    main()
