import os

import pandas as pd


REPO = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def round5(x):
    return round(x * 2) / 2


def main():
    path = os.path.join(REPO, 'external', 'tariffs', 'tariffs_99UI.xlsx')
    cols = ['module', 'cause', 'symptom', 'question', 'SmartVA', 'combined']
    df = pd.read_excel(path, sheetname='Tariffs')

    smartva_rounded = df.SmartVA.fillna(0).map(round5)
    combined_rounded = df.combined.fillna(0).map(round5)

    insignificant = (df.combined_lb * df.combined_ub <= 0)
    df.loc[insignificant, 'combined'] = 0

    df = df.loc[~(insignificant & (df.SmartVA == 0)) &
                ((smartva_rounded - combined_rounded).abs() > 0.5) &
                ~df.question.fillna('').str.startswith('word_') &
                (df.cause != 'Neonatal tetanus')
                , cols].sort_values(['module', 'cause', 'SmartVA'],
                                    ascending=[True, True, False])
    out_path = os.path.join(REPO, 'external', 'tariffs',
                            'significant_tariff_changes.csv')
    df.to_csv(out_path, index=False, encoding='utf8')


if __name__ == '__main__':
    main()
