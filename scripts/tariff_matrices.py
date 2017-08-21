import os
import sys

import numpy as np
import numexpr as ne
import pandas as pd

from getters import (
    REPO_DIR,
    get_codebook,
    get_smartva_symptoms,
    get_cause_map,
)


SVA_REPO = os.path.join(REPO_DIR, '..', 'smartva')
RAND = np.random.RandomState(8675309)


def get_data():
    modules = ['adult', 'child', 'neonate']

    path = os.path.join(REPO_DIR, 'external', 'data_release', 'gs_full.csv')
    gs = pd.read_csv(path).set_index('sid')
    stratifiers = {mod: gs.loc[gs.module == mod] for mod in modules}

    sva_output = os.path.join(REPO_DIR, 'data', 'smartva_output', 'gs_full')
    symptoms = {mod: get_smartva_symptoms(sva_output, mod) for mod in modules}

    cause_map = {mod: get_cause_map(mod, 'smartva', 'smartva_text')
                 for mod in modules}

    sys.path.insert(0, SVA_REPO)
    import smartva.data.adult_tariff_data as atd
    import smartva.data.child_tariff_data as ctd
    import smartva.data.neonate_tariff_data as ntd
    sys.path.remove(SVA_REPO)
    spurious = {
        'adult': atd.SPURIOUS_ASSOCIATIONS,
        'child': ctd.SPURIOUS_ASSOCIATIONS,
        'neonate': ntd.SPURIOUS_ASSOCIATIONS,
    }
    spurious = {mod: {cause_map[mod][k]: v for k, v in spurious[mod].items()} for mod in modules}

    codebooks = {mod: get_codebook('{}_symptom.csv'.format(mod))
                 for mod in modules}

    return codebooks, symptoms, stratifiers, spurious, cause_map


def tariff_from_endorsements(series):
    """Calculate tariffs from a series of endorsement rates

    Args:
        series: endorsement rates

    Returns:
        series: tariff scores
    """
    pct25, median, pct75 = np.percentile(series, [25, 50, 75])
    iqr = pct75 - pct25 or 0.001
    return ne.evaluate("(series - median) / iqr")


def calc_tariffs(X, y, name='value'):
    if not np.all((X == 1) | (X == 0)):
        raise ValueError("Not all values of X are binary")
    endorsements = X.groupby(y).mean()

    tariffs = endorsements.apply(tariff_from_endorsements, raw=True) \
                          .stack().reset_index()
    tariffs.columns = ['cause', 'symptom', name]

    endorsements = endorsements.stack().reset_index()
    endorsements.columns = ['cause', 'symptom', '{}_rate'.format(name)]

    return endorsements, tariffs


def all_tariffs(symptoms, gs, name='value', cond=None):
    modules = ['adult', 'child', 'neonate']
    out = []
    for mod in modules:
        if cond:
            idx = gs[mod].query(cond).index
        else:
            idx = gs[mod].index
        idx = idx.intersection(symptoms[mod].index)
        if not idx.any():
            continue
        X = symptoms[mod].loc[idx]
        y = gs[mod].loc[idx, 'gs_analytic']

        endorsements, tariffs = calc_tariffs(X, y, name=name)
        endorsements_ui, tariffs_ui = bootstrap_tariffs(X, y, 500, name=name)

        tariffs = tariffs.merge(tariffs_ui)
        endorsements = endorsements.merge(endorsements_ui)

        tariffs['module'] = mod
        endorsements['module'] = mod

        endorsed = X.groupby(y).sum().stack().reset_index()
        endorsed.columns = ['cause', 'symptom', '{}_o'.format(name)]
        endorsements = endorsed.merge(endorsements)

        out.append((endorsements, tariffs))
    return tuple(map(pd.concat, zip(*out)))


def bootstrap_tariffs(X, y, n=500, name='value'):
    if not np.all((X == 1) | (X == 0)):
        raise ValueError("Not all values of X are binary")

    colnames = ['cause', 'symptom', '{}_lb'.format(name), '{}_ub'.format(name)]

    def bootstrapped_endorsements(df):
        return df.iloc[RAND.randint(df.shape[0], size=df.shape[0] * n)] \
                 .groupby(np.repeat(np.arange(n), df.index.shape[0])).mean()

    def calc_ui(arr):
        return pd.Series(np.percentile(arr, (0.5, 99.5)), index=['lb', 'ub'])

    endorsements = X.groupby(y).apply(bootstrapped_endorsements)

    tariffs = endorsements.groupby(level=1) \
              .apply(lambda df: df.apply(tariff_from_endorsements, raw=True)) \
              .stack().groupby(level=[0, 2]).apply(calc_ui) \
              .unstack().reset_index()
    tariffs.columns = colnames

    endorsements = endorsements.stack().groupby(level=[0, 2]).apply(calc_ui) \
                               .unstack().reset_index()
    endorsements.columns = colnames

    return endorsements, tariffs


def main():
    modules = ['adult', 'child', 'neonate']
    codebook, symptoms, stratifiers, spurious, cause_map = get_data()
    sva_data = os.path.join(SVA_REPO, 'smartva', 'data')
    tariffs = []
    for mod in modules:

        df = pd.read_csv(os.path.join(sva_data, 'tariffs-{}.csv'.format(mod)),
                         index_col=0)
        df.index = df.index.str.lstrip('cause').astype(int).to_series() \
                     .map(cause_map[mod])
        df = df.stack().reset_index()
        df.columns = ['cause', 'symptom', 'SmartVA']
        df['cause_group'] = df.cause.map(CAUSE_AGG8[mod])

        symp = codebook[mod].reset_index()[['variable', 'question']]
        symp.columns = ['symptom', 'question']

        df = df.merge(symp, how='left', on='symptom')
        df['module'] = mod

        df['spurious']  = np.nan
        for cause, spurs in spurious[mod].items():
            spur_loc = (df.cause == cause) & (df.symptom.isin(spurs))
            df.loc[spur_loc, 'spurious'] = 'X'

        tariffs.append(df)
    tariffs = pd.concat(tariffs)
    tariffs = tariffs[['module', 'symptom', 'question', 'cause', 'cause_group',
                       'spurious', 'SmartVA']]
    endorsements = tariffs.drop('SmartVA', axis=1)

    common_cols = ['module', 'cause', 'symptom']

    endor, tar = all_tariffs(symptoms, stratifiers, 'combined')
    endorsements = endorsements.merge(endor, how='outer', on=common_cols)
    tariffs = tariffs.merge(tar, how='outer', on=common_cols)

    subsets = [
        ('phmrc', 'study=="PHMRC"'),
        ('nhmrc', 'study=="NHMRC"'),
        ('phmrc-AP', 'study=="PHMRC" & site=="AP"'),
        ('phmrc-UP', 'study=="PHMRC" & site=="UP"'),
        ('phmrc-Mexico', 'study=="PHMRC" & site=="Mexico"'),
        ('phmrc-Dar', 'study=="PHMRC" & site=="Dar"'),
        ('phmrc-Bohol', 'study=="PHMRC" & site=="Bohol"'),
        ('nhmrc-BGD', 'study=="NHMRC" & site=="BGD"'),
        ('nhmrc-PHL', 'study=="NHMRC" & site=="PHL"'),
        ('nhmrc-PNG', 'study=="NHMRC" & site=="PNG"'),
    ]

    for name, cond in subsets:
        endor, tar = all_tariffs(symptoms, stratifiers, name, cond)
        endorsements = endorsements.merge(endor, how='outer', on=common_cols)
        tariffs = tariffs.merge(tar, how='outer', on=common_cols)

    # Pandas set cell style on header cells which cannot be overwritten
    # by row and column formatting. Reset the Pandas formats before
    # writing headers
    pd.formats.format.header_style = None

    outfile = os.path.join(REPO_DIR, 'external', 'tariffs', 'tariffs_99UI.xlsx')
    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
    workbook = writer.book

    bold_fmt = workbook.add_format({'bold': True})
    rot_fmt = workbook.add_format({'rotation': 45})
    num_fmt = workbook.add_format({'num_format': '0.0'})
    pct_fmt = workbook.add_format({'num_format': '0.0%'})
    wrap_fmt = workbook.add_format({'text_wrap': True})

    sheet_name = 'Tariffs'
    tariffs.to_excel(writer, sheet_name=sheet_name, index=False)
    sheet = writer.sheets[sheet_name]
    sheet.set_row(0, None, bold_fmt)
    sheet.autofilter(0, 0, tariffs.shape[0], tariffs.shape[1] - 1)
    sheet.freeze_panes(1, 6)
    sheet.set_column(0, 0, 9.43)
    sheet.set_column(1, 1, 10.86)
    sheet.set_column(2, 2, 70.71, wrap_fmt)
    sheet.set_column(3, 3, 34.29)
    sheet.set_column(4, 4, 16.57)
    sheet.set_column(5, 5, 9.43)
    sheet.set_column(6, tariffs.shape[1] - 1, 8.43, num_fmt)
    for i in range(6, tariffs.shape[1]):
        sheet.write(0, i, tariffs.columns[i], rot_fmt)

    sheet_name = 'Endorsements'
    endorsements.to_excel(writer, sheet_name=sheet_name, index=False)
    sheet = writer.sheets[sheet_name]
    sheet.set_row(0, None, bold_fmt)
    sheet.autofilter(0, 0, endorsements.shape[0], endorsements.shape[1] - 1)
    sheet.freeze_panes(1, 6)
    sheet.set_column(0, 0, 9.43)
    sheet.set_column(1, 1, 10.86)
    sheet.set_column(2, 2, 70.71, wrap_fmt)
    sheet.set_column(3, 3, 34.29)
    sheet.set_column(4, 4, 16.57)
    sheet.set_column(5, 5, 9.43)
    for i in range(6, endorsements.shape[1], 4):
        sheet.set_column(i, i, 7.43)
        sheet.set_column(i + 1, i + 3, 7.43, pct_fmt)
        for j in range(4):
            col_num = i + j
            sheet.write(0, col_num, endorsements.columns[col_num], rot_fmt)

    writer.save()


CAUSE_AGG8 = {
    'adult': {
        'AIDS': 'Chronic Infectious',
        'AIDS with TB': 'Chronic Infectious',
        'Anemia': 'Maternal',
        'Asthma': 'NCD',
        'Bite of Venomous Animal': 'Injury',
        'Breast Cancer': 'Cancer',
        'Cervical Cancer': 'Cancer',
        'Cirrhosis': 'NCD',
        'Colorectal Cancer': 'Cancer',
        'COPD': 'NCD',
        'Diabetes with Coma': 'NCD',
        'Diabetes with Renal Failure': 'NCD',
        'Diabetes with Skin Infection/Sepsis': 'NCD',
        'Diarrhea/Dysentery': 'Infectious',
        'Drowning': 'Injury',
        'Epilepsy': 'Neuro',
        'Esophageal Cancer': 'Cancer',
        'Falls': 'Injury',
        'Fires': 'Injury',
        'Hemorrhage': 'Maternal',
        'Homicide': 'Injury',
        'Hypertensive Disorder': 'Maternal',
        'Acute Myocardial Infarction': 'Cardiovascular',
        'Congestive Heart Failure': 'Cardiovascular',
        'Inflammatory Heart Disease': 'Cardiovascular',
        'Leukemia': 'Cancer',
        'Lung Cancer': 'Cancer',
        'Lymphomas': 'Cancer',
        'Malaria': 'Infectious',
        'Other Cancers': 'Cancer',
        'Other Cardiovascular Diseases': 'Cardiovascular',
        'Other Digestive Diseases': 'NCD',
        'Other Infectious Diseases': 'Infectious',
        'Other Injuries': 'Injury',
        'Other Non-communicable Diseases': 'NCD',
        'Other Pregnancy-Related Deaths': 'Maternal',
        'Pneumonia': 'Infectious',
        'Poisonings': 'Injury',
        'Prostate Cancer': 'Cancer',
        'Renal Failure': 'NCD',
        'Road Traffic': 'Injury',
        'Sepsis': 'Maternal',
        'Stomach Cancer': 'Cancer',
        'Stroke': 'Neuro',
        'Suicide': 'Injury',
        'TB': 'Chronic Infectious',
    },
    'child': {
        'Bite of Venomous Animal': 'Injury',
        'Drowning': 'Injury',
        'Falls': 'Injury',
        'Fires': 'Injury',
        'Other Injuries': 'Injury',
        'Poisonings': 'Injury',
        'Road Traffic': 'Injury',
        'Violent Death': 'Injury',
        'AIDS': 'Infectious',
        'Diarrhea/Dysentery': 'Infectious',
        'Encephalitis': 'Infectious',
        'Hemorrhagic fever': 'Infectious',
        'Malaria': 'Infectious',
        'Measles': 'Infectious',
        'Meningitis': 'Infectious',
        'Other Infectious Diseases': 'Infectious',
        'Pneumonia': 'Infectious',
        'Sepsis': 'Infectious',
        'Other Cancers': 'NCD',
        'Other Cardiovascular Diseases': 'NCD',
        'Other Defined Causes of Child Deaths': 'NCD',
        'Other Digestive Diseases': 'NCD',
    },
    'neonate': {
        'Meningitis/Sepsis': 'Infectious',
        'Pneumonia': 'Infectious',
        'Congenital malformation': 'Neonatal',
        'Birth asphyxia': 'Neonatal',
        'Preterm Delivery': 'Neonatal',
        'Stillbirth': 'Stillbirth',
    }
}

if __name__ == '__main__':
    main()
