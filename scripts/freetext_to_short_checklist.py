import argparse
import os
import re
import pandas as pd
from stemming.porter2 import stem


ADULT_WORDS = {
    'adult_7_1': 'kidney',
    'adult_7_2': 'dialysis',
    'adult_7_3': 'fever',
    'adult_7_4': 'ami',
    'adult_7_5': 'heart',
    'adult_7_6': 'jaundice',
    'adult_7_7': 'liver',
    'adult_7_8': 'malaria',
    'adult_7_9': 'pneumonia',
    'adult_7_10': 'renal',
    'adult_7_11': 'suicide',
}

CHILD_WORDS = {
    'child_6_1': 'abdomen',
    'child_6_2': 'cancer',
    'child_6_3': 'dehydration',
    'child_6_4': 'dengue',
    'child_6_5': 'diarrhea',
    'child_6_6': 'fever',
    'child_6_7': 'heart',
    'child_6_8': 'jaundice',
    'child_6_9': 'pneumonia',
    'child_6_10': 'rash',
}


NEONATE_WORDS = {
    'neonate_6_1': 'asphyxia',
    'neonate_6_2': 'incubator',
    'neonate_6_3': 'lung',
    'neonate_6_4': 'pneumonia',
    'neonate_6_5': 'preterm',
    'neonate_6_6': 'distress',
}

WORD_SUBS = {
    'abdomin': 'abdomen',
    'abdominal': 'abdomen',
    'acute myocardial infarction': 'ami',
    'cancerous': 'cancer',
    'carcinoma': 'cancer',
    'delivery': 'deliver',
    'diarrheal': 'diarrhea',
    'pnuemonia': 'pneumonia',
    'premature': 'preterm',
    'prematurity': 'preterm',
}

WORD_MAPS = {
    'adult': ADULT_WORDS,
    'child': CHILD_WORDS,
    'neonate': NEONATE_WORDS,
}

TEXT_COLS = {
    'adult': 'adult_7_c',
    'child': 'child_6_c',
    'neonate': 'neonate_6_c',
}


def which_module(series):
    age_cols = ['gen_5_4a', 'gen_5_4b', 'gen_5_4c']
    years, months, days = series.loc[age_cols].fillna(0)
    age_days = years * 365 + months * 30 + days
    if age_days >= 12 * 365:
        return 'adult'
    elif age_days < 12 * 365 and age_days > 28:
        return 'child'
    else:
        return 'neonate'


def get_words(series):
    module = which_module(series)
    text = re.sub('[^a-z\s]', '',
                  series.fillna('').get(TEXT_COLS[module], '').lower())
    for k, v in WORD_SUBS.items():
        text.replace(k, v)
    words = [stem(word) for word in set(text.split())
             if word in WORD_MAPS[module].values()]
    return pd.Series({col: int(word in words)
                      for col, word in WORD_MAPS[module].items()})


def convert_freetext_to_checklist(df):
    words = df.apply(get_words, axis=1)
    df[words.columns] = words
    return df.drop(TEXT_COLS.values(), axis=1)


def main(infile, outfile):
    df = pd.read_csv(infile, encoding='utf8')
    df = convert_freetext_to_checklist(df)
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    df.to_csv(outfile, index=False, encoding='utf8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert the PHMRC Full Instrument open response columns '
                    'into PHMRC Shortened Instrument checklist columns.')
    parser.add_argument('infile', help='Location of a csv file with ODK data')
    parser.add_argument('outfile', help='Location of the output file')
    main(*vars(parser.parse_args()))
