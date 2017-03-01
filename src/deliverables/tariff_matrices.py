import os

import numpy as np
import numexpr as ne
import pandas as pd

from getters import (
    REPO_DIR,
    get_codebook,
    get_smartva_symptoms,
    get_cause_map,
)


def get_data():
    modules = ['adult', 'child', 'neonate']

    path = os.path.join(REPO_DIR, 'external', 'data_release', 'gs_full.csv')
    gs = pd.read_csv(path).set_index('sid')
    stratifiers = {mod: gs.loc[gs.module == mod] for mod in modules}

    path = os.path.join(REPO_DIR, 'data', 'smartva_output', 'gs_full')
    symptoms = {mod: get_smartva_symptoms(path, mod) for mod in modules}

    codebooks = {mod: get_codebook('{}_symptom.csv'.format(mod))
                 for mod in modules}

    return codebooks, symptoms, stratifiers


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


def calc_tariffs(X, y, name='tariff'):
    if not np.all((X == 1) | (X == 0)):
        raise ValueError("Not all values of X are binary")
    endorsements = X.groupby(y).mean()
    df = endorsements.apply(tariff_from_endorsements).stack().reset_index()
    df.columns = ['cause', 'symptom', name]
    return df


def all_tariffs(symptoms, gs, name='tariff', cond=None):
    modules = ['adult', 'child', 'neonate']
    tariffs = []
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
        df = calc_tariffs(X, y, name=name)
        df['module'] = mod
        df = df[['module', 'cause', 'symptom', name]]
        ui = bootstrap_tariffs(X, y, 500).reset_index()
        ui.columns = ['cause', 'symptom', '{}_lb'.format(name),
                      '{}_ub'.format(name)]
        df = df.merge(ui)
        tariffs.append(df)
    return pd.concat(tariffs)


def bootstrap_tariffs(X, y, n=500):
    if not np.all((X == 1) | (X == 0)):
        raise ValueError("Not all values of X are binary")

    rs = np.random.RandomState()

    def bootstrapped_endorsements(df):
        return df.iloc[rs.randint(df.shape[0], size=df.shape[0] * n)] \
                 .groupby(np.repeat(np.arange(n), df.index.shape[0])).mean()

    def calc_ui(arr):
        return pd.Series(np.percentile(arr, (2.5, 97.5)), index=['lb', 'ub'])

    return X.groupby(y).apply(bootstrapped_endorsements) \
            .groupby(level=1) \
            .apply(lambda df: df.apply(tariff_from_endorsements, raw=True)) \
            .stack().groupby(level=[0, 2]).apply(calc_ui).unstack()


def main():
    modules = ['adult', 'child', 'neonate']
    codebook, symptoms, stratifiers = get_data()
    sva = os.path.join(REPO_DIR, '..', 'smartva', 'smartva', 'data')

    cause_map = {mod: get_cause_map(mod, 'smartva', 'smartva_text')
                 for mod in modules}

    tariffs = []
    for mod in modules:

        df = pd.read_csv(os.path.join(sva, 'tariffs-{}.csv'.format(mod)),
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

        tariffs.append(df)
    df = pd.concat(tariffs)
    df = df[['module', 'symptom', 'question', 'cause', 'cause_group',
             'SmartVA']]

    common_cols = ['module', 'cause', 'symptom']

    combined = all_tariffs(symptoms, stratifiers, 'combined')
    df = df.merge(combined, how='outer', on=common_cols)

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
        ss = all_tariffs(symptoms, stratifiers, name, cond)
        df = df.merge(ss, how='outer', on=common_cols)

    outfile = os.path.join(REPO_DIR, 'external', 'tariffs', 'tariffs.csv')
    df.to_csv(outfile, index=False)


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
