"""Calculate CSMF for every country using GBD results.

Public-access results should be downloaded from the GBD results tool:
http://ghdx.healthdata.org/gbd-results-tool

The query should include 'cause' as the context, 'percent' as the metric,
and deaths as the measure for the latest year of data. Locations should
include all countries. Subnational and regional estimates are not necessary.
Ages should include all the most detailed non-overlapping age groups, including
detailed neonatal age groups. Sex should list only 'male' and 'female'. Causes
should include all level 2, 3, and 4 causes. Data should be downloaded with
names, not IDs.

This file maps the extracted csvs to the VA cause list for each module.

"""

import argparse
import logging
from pathlib import Path

import pandas as pd


LOG = logging.getLogger('gbd_causes')
GBD_DATA_DIR = (Path(__file__) / '..' / '..' / 'data' / 'gbd').resolve()
URL = ('http://ghdx.healthdata.org/gbd-results-tool?params='
       'querytool-permalink/ae87fb91f81780d7908991e106a67ab3')
MODULES = ('adult', 'child', 'neonate')


def clean_gbd_data(input_dir=None):
    """
    """
    try:
        input_dir = Path(input_dir).resolve()
    except TypeError:
        LOG.debug(f'Loading data from {GBD_DATA_DIR}')
        input_dir = GBD_DATA_DIR

    try:
        loc_path = next(input_dir.glob('*LOCATION_HIERARCHIES*.csv'))
    except StopIteration:
        raise FileNotFoundError(f'Cannot find location hierarchy file in {input_dir}')

    LOG.info('Loading locations hierarchy: %s', loc_path.name)
    loc_hierarchy = pd.read_csv(loc_path)
    iso3s = dict(zip(loc_hierarchy.location_name, loc_hierarchy.location_code))

    paths = list(input_dir.glob('IHME-GBD_201*_DATA-*.csv'))
    LOG.info('Loading GBD data: %s', [p.name for p in paths])
    df = pd.concat([pd.read_csv(f) for f in paths])

    df.sex = df.sex.map({'Male': 1, 'Female': 2}).astype(int)
    df['iso3'] = df.location.map(iso3s)
    df.age = df.age.map(lambda x: x.split()[0])

    cols = ['iso3', 'age', 'sex', 'cause', 'val']
    if df[cols].isnull().any().any():
        raise ValueError

    return df[cols]


def calc_gbd_cause_fractions(df, modules=None):
    idx_cols = ['iso3', 'age', 'sex', 'cause']
    nn_ages = {
        'adult': {'Early': -9, 'Late': -9, 'Post': -9},
        'child': {'Early': -9, 'Late': -9, 'Post': 0},
        'neonate': {'Early': 0, 'Late': 7, 'Post': -9},
    }
    ages = {
        'adult': list(range(10, 81, 5)),
        'child': [0, 1, 5, 10],
        'neonate': [0, 7],
    }

    weights = {}
    for module in modules or MODULES:
        mapped = df.copy()

        mapped.age = mapped.age.replace(nn_ages[module]).astype(int)
        mapped = mapped.loc[mapped.age.isin(ages[module])]

        mapped.cause = mapped.cause.map(CAUSE_MAP[module])
        mapped = mapped.dropna().groupby(idx_cols, as_index=False).val.sum()

        agg = mapped.groupby(['iso3', 'cause'], as_index=False).sum()
        agg['age'] = 99
        agg['sex'] = 3

        weights[module] = pd.concat([mapped, agg]).set_index(idx_cols)

    return weights


def main(input_dir, output_dir, modules=None):
    df = clean_gbd_data(input_dir)
    csmf = calc_gbd_cause_fractions(df, modules)
    try:
        output_dir = Path(output_dir)
    except TypeError:
        output_dir = GBD_DATA_DIR
    for module, df in csmf.items():
        out_path = output_dir / f'{module}-gbd-csmf.csv'
        LOG.info('Saving : %s', out_path)
        df.to_csv(out_path, encoding='utf8')


ADULT_CAUSE_MAP = {
    'Tuberculosis': 'TB',
    'HIV/AIDS': 'AIDS',
    'Diarrheal diseases': 'Diarrhea/Dysentery',
    'Lower respiratory infections': 'Pneumonia',
    'Malaria': 'Malaria',

    'Intestinal infectious diseases': 'Other Infectious Diseases',
    'Upper respiratory infections': 'Other Infectious Diseases',
    'Otitis media': 'Other Infectious Diseases',
    'Encephalitis': 'Other Infectious Diseases',
    'Diphtheria': 'Other Infectious Diseases',
    'Whooping cough': 'Other Infectious Diseases',
    'Tetanus': 'Other Infectious Diseases',
    'Measles': 'Other Infectious Diseases',
    'Varicella and herpes zoster': 'Other Infectious Diseases',
    'Chagas disease': 'Other Infectious Diseases',
    'Leishmaniasis': 'Other Infectious Diseases',
    'Visceral leishmaniasis': 'Other Infectious Diseases',
    'Cutaneous and mucocutaneous leishmaniasis': 'Other Infectious Diseases',
    'African trypanosomiasis': 'Other Infectious Diseases',
    'Schistosomiasis': 'Other Infectious Diseases',
    'Cysticercosis': 'Other Infectious Diseases',
    'Cystic echinococcosis': 'Other Infectious Diseases',
    'Lymphatic filariasis': 'Other Infectious Diseases',
    'Onchocerciasis': 'Other Infectious Diseases',
    'Trachoma': 'Other Infectious Diseases',
    'Dengue': 'Other Infectious Diseases',
    'Yellow fever': 'Other Infectious Diseases',
    'Rabies': 'Other Infectious Diseases',
    'Intestinal nematode infections': 'Other Infectious Diseases',
    'Ascariasis': 'Other Infectious Diseases',
    'Trichuriasis': 'Other Infectious Diseases',
    'Hookworm disease': 'Other Infectious Diseases',
    'Food-borne trematodiases': 'Other Infectious Diseases',
    'Leprosy': 'Other Infectious Diseases',
    'Ebola': 'Other Infectious Diseases',
    'Other neglected tropical diseases': 'Other Infectious Diseases',
    'Other communicable, maternal, neonatal, and nutritional diseases': 'Other Infectious Diseases',

    'Maternal disorders': 'Maternal',
    'Iron-deficiency anemia': 'Maternal',

    'Protein-energy malnutrition': 'Other Non-communicable Diseases',
    'Iodine deficiency': 'Other Non-communicable Diseases',
    'Vitamin A deficiency': 'Other Non-communicable Diseases',
    'Iron-deficiency anemia': 'Other Non-communicable Diseases',
    'Other nutritional deficiencies': 'Other Non-communicable Diseases',


    'Esophageal cancer': 'Esophageal Cancer',
    'Stomach cancer': 'Stomach Cancer',
    'Tracheal, bronchus, and lung cancer': 'Lung Cancer',
    'Breast cancer': 'Breast Cancer',
    'Hodgkin lymphoma': 'Leukemia/Lymphomas',
    'Non-Hodgkin lymphoma': 'Leukemia/Lymphomas',
    'Leukemia': 'Leukemia/Lymphomas',
    'Prostate cancer': 'Prostate Cancer',
    'Cervical cancer': 'Cervical Cancer',
    'Colon and rectum cancer': 'Colorectal Cancer',

    'Liver cancer': 'Other Cancers',
    'Lip and oral cavity cancer': 'Other Cancers',
    'Nasopharynx cancer': 'Other Cancers',
    'Other pharynx cancer': 'Other Cancers',
    'Gallbladder and biliary tract cancer': 'Other Cancers',
    'Pancreatic cancer': 'Other Cancers',
    'Larynx cancer': 'Other Cancers',
    'Malignant skin melanoma': 'Other Cancers',
    'Non-melanoma skin cancer': 'Other Cancers',
    'Uterine cancer': 'Other Cancers',
    'Ovarian cancer': 'Other Cancers',
    'Testicular cancer': 'Other Cancers',
    'Kidney cancer': 'Other Cancers',
    'Bladder cancer': 'Other Cancers',
    'Brain and nervous system cancer': 'Other Cancers',
    'Thyroid cancer': 'Other Cancers',
    'Mesothelioma': 'Other Cancers',
    'Multiple myeloma': 'Other Cancers',
    'Other neoplasms': 'Other Cancers',

    'Cerebrovascular disease': 'Stroke',
    'Ischemic heart disease': 'Ischemic Heart Disease',

    'Rheumatic heart disease': 'Other Cardiovascular Diseases',
    'Hypertensive heart disease': 'Other Cardiovascular Diseases',
    'Cardiomyopathy and myocarditis': 'Other Cardiovascular Diseases',
    'Atrial fibrillation and flutter': 'Other Cardiovascular Diseases',
    'Aortic aneurysm': 'Other Cardiovascular Diseases',
    'Peripheral vascular disease': 'Other Cardiovascular Diseases',
    'Endocarditis': 'Other Cardiovascular Diseases',
    'Other cardiovascular and circulatory diseases': 'Other Cardiovascular Diseases',

    'Chronic obstructive pulmonary disease': 'Chronic Respiratory',
    'Pneumoconiosis': 'Chronic Respiratory',
    'Asthma': 'Chronic Respiratory',

    'Interstitial lung disease and pulmonary sarcoidosis': 'Other Non-communicable Diseases',
    'Other chronic respiratory diseases': 'Other Non-communicable Diseases',

    'Cirrhosis and other chronic liver diseases': 'Cirrhosis',
    'Digestive diseases': 'Other Non-communicable Diseases',

    'Epilepsy': 'Other Non-communicable Diseases',
    'Alzheimer disease and other dementias': 'Other Non-communicable Diseases',
    'Parkinson disease': 'Other Non-communicable Diseases',
    'Multiple sclerosis': 'Other Non-communicable Diseases',
    'Motor neuron disease': 'Other Non-communicable Diseases',
    'Migraine': 'Other Non-communicable Diseases',
    'Tension-type headache': 'Other Non-communicable Diseases',
    'Medication overuse headache': 'Other Non-communicable Diseases',
    'Other neurological disorders': 'Other Non-communicable Diseases',
    'Mental and substance use disorders': 'Other Non-communicable Diseases',

    'Diabetes mellitus': 'Diabetes',
    'Chronic kidney disease due to diabetes mellitus': 'Diabetes',
    'Acute glomerulonephritis': 'Renal Failure',
    'Chronic kidney disease due to hypertension': 'Renal Failure',
    'Chronic kidney disease due to glomerulonephritis': 'Renal Failure',
    'Chronic kidney disease due to other causes': 'Renal Failure',

    'Urinary diseases and male infertility': 'Other Non-communicable Diseases',
    'Gynecological diseases': 'Other Non-communicable Diseases',
    'Hemoglobinopathies and hemolytic anemias': 'Other Non-communicable Diseases',
    'Endocrine, metabolic, blood, and immune disorders': 'Other Non-communicable Diseases',
    'Musculoskeletal disorders': 'Other Non-communicable Diseases',
    'Other non-communicable diseases': 'Other Non-communicable Diseases',

    'Road injuries': 'Road Traffic',
    'Falls': 'Falls',
    'Drowning': 'Drowning',
    'Fire, heat, and hot substances': 'Fires',
    'Poisonings': 'Poisonings',
    'Animal contact': 'Bite of Venomous Animal',
    'Self-harm': 'Suicide',
    'Interpersonal violence': 'Homicide',

    'Other transport injuries': 'Other Injuries',
    'Exposure to mechanical forces': 'Other Injuries',
    'Adverse effects of medical treatment': 'Other Injuries',
    'Foreign body': 'Other Injuries',
    'Environmental heat and cold exposure': 'Other Injuries',
    'Other unintentional injuries': 'Other Injuries',
    'Forces of nature, war, and legal intervention': 'Other Injuries',
}

CHILD_CAUSE_MAP = {
    'HIV/AIDS': 'AIDS',
    'Diarrheal diseases': 'Diarrhea/Dysentery',
    'Lower respiratory infections': 'Pneumonia',
    'Malaria': 'Malaria',
    'Meningitis': 'Meningitis',
    'Encephalitis': 'Encephalitis',
    'Measles': 'Measles',
    'Dengue': 'Hemorrhagic fever',
    'Yellow fever': 'Hemorrhagic fever',

    'Tuberculosis': 'Other Infectious Diseases',
    'Intestinal infectious diseases': 'Other Infectious Diseases',
    'Upper respiratory infections': 'Other Infectious Diseases',
    'Otitis media': 'Other Infectious Diseases',
    'Diphtheria': 'Other Infectious Diseases',
    'Whooping cough': 'Other Infectious Diseases',
    'Tetanus': 'Other Infectious Diseases',
    'Varicella and herpes zoster': 'Other Infectious Diseases',
    'Chagas disease': 'Other Infectious Diseases',
    'Leishmaniasis': 'Other Infectious Diseases',
    'Visceral leishmaniasis': 'Other Infectious Diseases',
    'Cutaneous and mucocutaneous leishmaniasis': 'Other Infectious Diseases',
    'African trypanosomiasis': 'Other Infectious Diseases',
    'Schistosomiasis': 'Other Infectious Diseases',
    'Cysticercosis': 'Other Infectious Diseases',
    'Cystic echinococcosis': 'Other Infectious Diseases',
    'Lymphatic filariasis': 'Other Infectious Diseases',
    'Onchocerciasis': 'Other Infectious Diseases',
    'Trachoma': 'Other Infectious Diseases',
    'Rabies': 'Other Infectious Diseases',
    'Intestinal nematode infections': 'Other Infectious Diseases',
    'Ascariasis': 'Other Infectious Diseases',
    'Trichuriasis': 'Other Infectious Diseases',
    'Hookworm disease': 'Other Infectious Diseases',
    'Food-borne trematodiases': 'Other Infectious Diseases',
    'Leprosy': 'Other Infectious Diseases',
    'Ebola': 'Other Infectious Diseases',
    'Other neglected tropical diseases': 'Other Infectious Diseases',
    'Other communicable, maternal, neonatal, and nutritional diseases': 'Other Infectious Diseases',

    'Neoplasms': 'Other Cancers',
    'Cardiovascular diseases': 'Other Cardiovascular Diseases',
    'Digestive diseases': 'Other Digestive Diseases',
    'Cellulitis': 'Sepsis',
    'Abscess, impetigo, and other bacterial skin diseases': 'Sepsis',


    'Chronic respiratory diseases': 'Other Defined Causes of Child Deaths',
    'Neonatal disorders': 'Other Defined Causes of Child Deaths',
    'Nutritional deficiencies': 'Other Defined Causes of Child Deaths',
    'Cirrhosis and other chronic liver diseases': 'Other Defined Causes of Child Deaths',
    'Neurological disorders': 'Other Defined Causes of Child Deaths',
    'Mental and substance use disorders': 'Other Defined Causes of Child Deaths',
    'Diabetes, urogenital, blood, and endocrine diseases': 'Other Defined Causes of Child Deaths',
    'Musculoskeletal disorders': 'Other Defined Causes of Child Deaths',
    'Other non-communicable diseases': 'Other Defined Causes of Child Deaths',

    'Road injuries': 'Road Traffic',
    'Falls': 'Falls',
    'Drowning': 'Drowning',
    'Fire, heat, and hot substances': 'Fires',
    'Poisonings': 'Poisonings',
    'Animal contact': 'Bite of Venomous Animal',
    'Interpersonal violence': 'Violent Death',

    'Other transport injuries': 'Other Defined Causes of Child Deaths',
    'Exposure to mechanical forces': 'Other Defined Causes of Child Deaths',
    'Adverse effects of medical treatment': 'Other Defined Causes of Child Deaths',
    'Foreign body': 'Other Defined Causes of Child Deaths',
    'Environmental heat and cold exposure': 'Other Defined Causes of Child Deaths',
    'Other unintentional injuries': 'Other Defined Causes of Child Deaths',
    'Forces of nature, war, and legal intervention': 'Other Defined Causes of Child Deaths',
}

NEONATE_CAUSE_MAP = {
    'Lower respiratory infections': 'Pneumonia',
    'Meningitis': 'Meningitis/Sepsis',
    'Neonatal preterm birth complications': 'Preterm Delivery',
    'Neonatal encephalopathy due to birth asphyxia and trauma': 'Birth asphyxia',
    'Neonatal sepsis and other neonatal infections': 'Meningitis/Sepsis',
    'Congenital birth defects': 'Congenital malformation'
}

CAUSE_MAP = {
    'adult': ADULT_CAUSE_MAP,
    'child': CHILD_CAUSE_MAP,
    'neonate': NEONATE_CAUSE_MAP,
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Map downloaded GBD results to the VA cause list.')
    parser.add_argument('-i', '--input_dir',
                        help='Directory of unzipped csv files download from '
                             'the GBD results tool')
    parser.add_argument('-o', '--output_dir',
                        help='Directory to save mapped files')
    parser.add_argument('-m', '--modules', nargs='*', type=str.lower,
                        choices=MODULES, default=MODULES)
    parser.add_argument('--log-level', type=str.upper, default='INFO',
                        choices=('DEBUG', 'INFO', 'WARN', 'CRITICAL'))
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level))
    LOG.debug(args)
    main(args.input_dir, args.output_dir, args.modules)
