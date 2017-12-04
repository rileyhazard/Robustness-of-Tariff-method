"""Create matrices of tariffs and endorsements from various input data.

Paper: Robustness of the Tariff method for diagnosing verbal autopsies
Data from: https://cloud.ihme.washington.edu/remote.php/webdav/VA_ODK_FILES
Data file: va_gold_standard_database.csv

Code in this file is used to
"""
from collections import OrderedDict
from functools import partial
from importlib import import_module
import logging
from pathlib import Path
import sys
import subprocess

import click
import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO))
from tariff2 import tariff, validation


MODULES = ('adult', 'child', 'neonate')
INPUT_FILE = REPO / 'data/va_gold_standard_database.csv'
OUT_DIR = REPO / 'data/new_tariffs'
SMARTVA_OUTPUT = OUT_DIR / 'smartva'
OUTPUT_FILE = OUT_DIR / 'tariffs.csv'
SMARTVA_REPO = REPO.parent / 'smartva'

fmt_blue = partial(click.style, bold=True, fg='blue')
fmt_magenta = partial(click.style, bold=True, fg='magenta')


SUBSETS = OrderedDict([
    ('combined', None),
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
])
UI = (0.5, 99.5)   # 99% UI


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    if ctx.invoked_subcommand is None:
        run_smartva()
        df = main_tariffs()
        write_excel_report(df)
        write_important_tariffs(df)
        main_performance()


def _find_smartva_conda_env(env='smartva'):
    """Find python installation suitable for running smartva.

    The code in this file has imports that are not included the environment
    used to run SmartVA. Likewise, SmartVA as requirements that are not
    included in this project. I'm assuming python installations are managed
    by conda (instead of virtualenv or manually).
    """
    res = subprocess.run('conda info --envs'.split(), check=True,
                         stdout=subprocess.PIPE)
    for line in res.stdout.decode().split('\n'):
        if line.startswith('#'):
            continue
        path = line.split()[-1]
        if path.endswith(env):
            return Path(path)
    logging.warning(f'Cannot find "{env}" among conda enviroments')


def run_smartva(env='smartva', repo=SMARTVA_REPO, output_dir=SMARTVA_OUTPUT):
    """Run the gold standard database through SmartVA.

    We're really only using SmartVA for the feature extraction. We don't
    care about the predictions for this excerise. We're planning on making
    our own.
    """
    env = _find_smartva_conda_env(env)
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = f'{env}/bin/python {repo}/app.py {INPUT_FILE} {output_dir}'
    subprocess.run(cmd.split(), stdout=subprocess.PIPE)


@cli.command()
@click.option('--env', default='smartva', help='conda environment name')
@click.option('--repo', default=SMARTVA_REPO, help='Path to SmartVA repo')
@click.option('-o', '--output_dir', help='Output directory for SmartVA',
              type=click.Path(file_okay=False, dir_okay=True, writable=True),
              default=SMARTVA_OUTPUT)
def smartva(env, repo, output_dir):
    """Run SmartVA to process symptoms"""
    run_smartva(env, repo, output_dir)


def select_X_y(symptoms, gs, cause_col='gs_analytic', cause_map=None,
               condition=None):
    """Filter rows in paired data based on a condition.

    Condtions are tested against the values in the gold standard dataframe.

    Args:
        symptoms (dataframe): symptom data indexed on sid
        gs (dataframe): gold standards indexed on sid with cause_col
        cause_col (str): column name in gs
        cause_map: passed to pd.Series.map for the causes in cause_col
        condition (str): passed to pd.DataFrame.query on gs

    Returns:
        tuple: matched observations of symptoms (dataframe), causes (series)
    """
    idx = gs.query(condition).index if condition else gs.index
    if idx.empty and condition:
        raise IndexError(f'No values satisfy the query: `{condition}`')
    idx = idx.intersection(symptoms.index)

    causes = gs.loc[idx, cause_col]
    if cause_map is not None:
        causes = causes.map(cause_map)

    return symptoms.loc[idx], causes


def calc_tariffs_and_endorsement_rates(X, y, bootstraps, ui=UI, rs=None):
    """Calculate tariffs and endorsement rates.

    For these results, we want raw tariffs where we haven't dropped or rounded
    any values. We also want to save the endorsement rates, which usually are
    an intermediate product.

    This function calculates UI for both endorsement rates and tariffs and
    returns a multiindex dataframe long on cause and symptom with six columns:
    point estimate and upper and lower bounds for both endorsements and
    tariffs.
    """
    endors = X.groupby(y).mean()
    tariffs = tariff.calc_tariffs(X, y)

    bs_endors = tariff.boostrap_endorsements_by_causes(X, y, bootstraps, rs) \
                      .swaplevel(0, 1).sort_index()
    bs_tariffs = bs_endors.groupby(level='draw').apply(
        lambda df: df.apply(tariff.tariffs_from_endorsements, raw=True))

    endors_lb, endors_ub = np.percentile(
        np.dstack([bs_endors.loc[i].values for i in range(bootstraps)]),
        ui, -1)
    tariffs_lb, tariffs_ub = np.percentile(
        np.dstack([bs_tariffs.loc[i].values for i in range(bootstraps)]),
        ui, -1)

    names = ('tariff', 'tariff_lb', 'tariff_ub', 'endorsement_rate',
             'endorsement_rate_lb', 'endorsement_rate_ub')
    arrs = (tariffs, tariffs_lb, tariffs_ub, endors, endors_lb, endors_ub)
    df = pd.concat([
        pd.DataFrame(arr, endors.index, endors.columns)
          .assign(name=name).set_index('name', append=True)
        for name, arr in zip(names, arrs)
    ]).sort_index().stack().unstack('name').rename_axis(['cause', 'symptom'])
    return df


def load_spurious_asscociations(module, repo=SMARTVA_REPO):
    """Load spurious associations from the SmartVA repo"""
    try:
        sys.path.insert(0, str(SMARTVA_REPO))
        tariff_data = import_module(f'smartva.data.{module}_tariff_data',
                                    package='smartva')
    except ImportError as e:
        raise FileNotFoundError(f'Cannot find SmartVA repo at {SMARTVA_REPO}')\
            from e
    finally:
        sys.path.remove(str(SMARTVA_REPO))
    return {tariff_data.CAUSES46[k]: v
            for k, v in tariff_data.SPURIOUS_ASSOCIATIONS.items()}


def load_cause_map(module):
    return yaml.load((HERE / 'cause_map.yml').read_text())[module]


def load_cause_groups(module):
    """Load aggregated cause groups.

    These are only used for reporting and filtering results. They have
    no analytic purpose.
    """
    return yaml.load((HERE / 'cause_groups.yml').read_text())[module]


def load_symptom_descriptions(module):
    """Load symptoms from the codebooks in this repo."""
    return pd.read_csv(REPO / f'codebooks/{module}_symptom.csv', index_col=0)\
             .question


def load_smartva_output(module, path=SMARTVA_OUTPUT):
    """Load only symptom columns from Smartva intermediate files"""
    filepath = path / f'intermediate-files/{module}-symptom.csv'
    logging.info(fmt_blue('Loading: ') + str(filepath))
    return pd.read_csv(filepath, index_col=0) \
             .filter(regex='^age$|^sex$|^s\d+$').fillna(0)


def load_gold_standards(path=INPUT_FILE):
    """Load the data file with gold standards.

    We are only loading a subset of columns. These columns are useful for
    stratifying the dataset and calculating tariff with different subsets
    for comparison purposes.
    """
    logging.info(fmt_blue('Loading: ') + str(path))
    cols = ['sid', 'study', 'site', 'module', 'gs_analytic', 'gs_level']
    df = pd.read_csv(path, index_col='sid', usecols=cols)
    df = df.loc[df.gs_analytic != 'Neonatal tetanus']
    return df


def main_tariffs():
    """Run the primary analysis calculating tariffs."""
    output = []
    gold_standards = load_gold_standards()
    bootstraps = 500
    rs = np.random.RandomState(2301598125)

    for module in MODULES:
        logging.info(f'Processing {module} data')
        symptom_descriptions = load_symptom_descriptions(module)
        spurious = load_spurious_asscociations(module)
        cause_groups = load_cause_groups(module)
        symptoms = load_smartva_output(module)

        dfs = []
        for name, condition in SUBSETS.items():
            logging.info(f'    Calculating tariffs for {name}')
            X, y = select_X_y(symptoms, gold_standards, condition=condition)
            df = calc_tariffs_and_endorsement_rates(X, y, bootstraps, UI, rs)
            df.columns = pd.MultiIndex.from_arrays([
                np.full(6, name),
                np.repeat(['endorsement_rate', 'tariff'], 3),
                np.tile(['value', 'lower', 'upper'], 2)
            ], names=('subset', 'measure', 'point'))
            dfs.append(df)
        df = pd.concat(dfs, axis=1)
        df['module'] = module
        df['cause_group'] = df.index.get_level_values('cause') \
                              .map(cause_groups.get)
        df['description'] = df.index.get_level_values('symptom') \
                              .map(symptom_descriptions.get)
        df['spurious'] = np.nan
        for cause, symps in spurious.items():
            for symp in symps:
                df.loc[(cause, symp), 'spurious'] = 'X'

        add_idx = ['module', 'cause_group', 'description', 'spurious']
        order = ['module', 'symptom', 'description', 'cause', 'cause_group',
                 'spurious']
        df = df.set_index(add_idx, append=True).reorder_levels(order)

        output.append(df)

    df = pd.concat(output)
    logging.info(fmt_magenta('Saving: ') + str(OUTPUT_FILE))
    df.apply(np.round, decimals=2).to_csv(OUTPUT_FILE)
    return df


@cli.command()
@click.option('--main', is_flag=True, help='Run only the main analysis')
@click.option('-m', 'module', type=click.Choice(MODULES))
@click.option('-c', '--condition', help='query string')
@click.option('-d', '--draws', default=100)
@click.option('--seed', type=int, default=2301598125)
@click.pass_context
def tariffs(ctx, main, module, condition, draws, seed):
    """Make tariff matricies"""
    if main:
        main_tariffs()
        ctx.exit()
    symptoms = load_smartva_output(module)
    gold_standards = load_gold_standards()
    X, y = select_X_y(symptoms, gold_standards, condition=condition)
    df = calc_tariffs_and_endorsement_rates(X, y, draws, seed)
    print(np.round(df, 3))


def calc_performance(module, n_splits=10, condition=None):
    symptoms = load_smartva_output(module)
    gold_standards = load_gold_standards()
    cause_map = load_cause_map(module)
    X, y = select_X_y(symptoms, gold_standards, cause_map=cause_map,
                      condition=condition)
    splits = validation.out_of_sample_splits(X, y, n_splits=n_splits)
    clf = tariff.TariffClassifier(tariffs_ui=99)
    return validation.validate_splits(X, y, clf, splits)


def main_performance():
    gold_standards = load_gold_standards()
    n_splits = 3
    out_dir = OUT_DIR / 'performance'
    out_dir.mkdir(parents=True, exist_ok=True)

    for module in MODULES:
        symptoms = load_smartva_output(module)
        cause_map = load_cause_map(module)
        logging.info(f'Calculating performance for {module} data')

        output = []
        for condition in (None, 'study=="PHMRC"'):
            name = 'combined' if not condition else 'phmrc'
            logging.info(f'    ...using {name} dataset')

            X, y = select_X_y(symptoms, gold_standards, cause_map=cause_map,
                              condition=condition)
            splits = validation.out_of_sample_splits(X, y, n_splits=n_splits)
            clf = tariff.TariffClassifier(tariffs_ui=99)
            dfs = validation.validate_splits(X, y, clf, splits)

            output.append([df.assign(study=name, module=module) for df in dfs])

        dfs = map(pd.concat, zip(*output))
        names = ('predictions', 'csmf', 'ccc', 'accuracy')
        for name, df in zip(names, dfs):
            outfile = out_dir / f'{module}-{name}.csv'
            logging.info(fmt_magenta('Saving: ') + str(outfile))
            df.to_csv(outfile, index=False)


@cli.command()
@click.option('--main', is_flag=True, help='Run only the main analysis')
@click.option('-m', 'module', type=click.Choice(MODULES))
@click.option('-c', '--condition', help='query string')
@click.pass_context
def performance(ctx, main, module, condition):
    """Run performance analysis"""
    if main:
        main_performance()
        ctx.exit()
    preds, csmf, ccc, accuracy = calc_performance(module, condition)
    print(accuracy.drop('split', axis=1).mean())


def load_output_file():
    logging.info(fmt_blue('Loading: ') + str(OUTPUT_FILE))
    return pd.read_csv(OUTPUT_FILE, header=[0, 1, 2], index_col=list(range(6)))


@cli.group()
def tables():
    """Generate tables from results"""
    pass


def write_excel_report(df, outfile=None):
    # Pandas set cell style on header cells which cannot be overwritten
    # by row and column formatting. Reset the Pandas formats before
    # writing headers
    # pd.io.formats.format.header_style = None

    df = df.rename(columns=lambda x: '' if x == 'value' else f'_{x[0]}b',
                   level='point')
    tariffs = df.xs('tariff', level='measure', axis='columns')
    endorsements = df.xs('endorsement_rate', level='measure', axis='columns')

    tariffs.columns = [f'{name}{p}' for name, p in tariffs.columns.tolist()]
    endorsements.columns = tariffs.columns

    tariffs = tariffs.reset_index()
    endorsements = endorsements.reset_index()

    # TODO: add series of columns for number of endorsements

    outfile = outfile or str(OUTPUT_FILE).replace('.csv', '.xlsx')
    writer = pd.ExcelWriter(outfile, engine='xlsxwriter')
    workbook = writer.book

    bold_fmt = workbook.add_format({'bold': True})
    rot_fmt = workbook.add_format({'rotation': 45})
    num_fmt = workbook.add_format({'num_format': '0.0'})
    pct_fmt = workbook.add_format({'num_format': '0.0%'})
    wrap_fmt = workbook.add_format({'text_wrap': True})

    logging.info('    Formating Tariffs sheet')
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

    logging.info('    Formating Endorsements sheet')
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
    for i in range(6, endorsements.shape[1], 3):
        sheet.set_column(i, i, 7.43)
        sheet.set_column(i, i + 3, 7.43, pct_fmt)
        for j in range(3):
            col_num = i + j
            sheet.write(0, col_num, endorsements.columns[col_num], rot_fmt)

    logging.info(fmt_magenta('Saving: ') + str(outfile))
    writer.save()


@tables.command()
@click.option('-o', '--outfile', type=click.Path(file_okay=True, exists=True))
def complete(outfile):
    df = load_output_file()
    write_excel_report(df, outfile)


def write_important_tariffs(df, outfile=None):
    outfile = Path(outfile) if outfile else OUT_DIR / 'important.csv'

    df = df.xs('tariff', level='measure', axis='columns')

    def round5(x):
        return round(x * 2) / 2

    phmrc = df.phmrc.value.fillna(0).map(round5)
    combined = df.combined.value.fillna(0).map(round5)

    phmrc.loc[(df.phmrc.lower * df.phmrc.upper <= 0)] = 0
    combined.loc[(df.combined.lower * df.combined.upper <= 0)] = 0

    not_word = ~df.index.get_level_values('description') \
                  .fillna('').str.startswith('word_')
    important = (phmrc != 0) & (combined != 0) & (phmrc - combined).abs() > 0.5

    df = df.loc[important & not_word] \
           .xs('value', level='point', axis='columns')[['phmrc', 'combined']]\
           .reset_index() \
           .sort_values(['module', 'cause', 'phmrc'],
                        ascending=[True, True, False])
    logging.info(fmt_magenta('Saving: ') + str(outfile))
    df.to_csv(outfile, index=False, encoding='utf8')


@tables.command()
@click.option('-o', '--outfile', type=click.Path(file_okay=True, exists=True))
def important(outfile):
    df = load_output_file()
    write_important_tariffs(df, outfile)


if __name__ == '__main__':
    cli()
