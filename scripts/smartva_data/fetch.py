from functools import partial
import logging
from pathlib import Path
import shutil

import click
import pandas as pd


MODULES = ('adult', 'child', 'neonate')
REPO = Path(__file__).resolve().parent.parent.parent
SMARTVA_REPO = REPO.parent / 'smartva'
OUT_DIR = REPO / 'data/smartva'

fmt_blue = partial(click.style, bold=True, fg='blue')
fmt_magenta = partial(click.style, bold=True, fg='magenta')


@click.group(chain=True)
@click.option('--repo', help='SmartVA repo',
              type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('-m', '--module', type=click.Choice(MODULES), multiple=True)
@click.pass_context
def cli(ctx, repo, module):
    """Fetch SmartVA data from the source code."""
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    smartva_repo = Path(repo) if repo else SMARTVA_REPO
    if not smartva_repo.exists():
        raise FileNotFoundError(f'Cannot find SmartVA repo: {smartva_repo}')

    ctx.obj = {}
    ctx.obj['smartva_data'] = smartva_repo / 'smartva/data'
    ctx.obj['modules'] = module or MODULES
    ctx.obj['out_dir'] = OUT_DIR / 'smartva'


@cli.command(short_help='Copy tariff matrices.')
@click.pass_context
def tariffs(ctx):
    """Copy tariff matrices from SmartVA source code as is."""
    ctx.obj['out_dir'].mkdir(parents=True, exist_ok=True)
    for module in ctx.obj['modules']:
        filepath = ctx.obj['smartva_data'] / f'tariffs-{module}.csv'
        outfile = ctx.obj['out_dir'] / f'smartva-{filepath.name}'
        logging.info(fmt_blue('Copying: ') + f'{filepath} to {outfile}')
        shutil.copyfile(str(filepath), str(outfile))


def calc_smartva_endorsement_rates(df, module):
    cause_col = 'gs_text34' if module == 'neonate' else 'gs_text46'

    drop_cols = df.filter(regex='^gs|^va|sid|site').columns.tolist()
    drop_cols.remove(cause_col)
    df = df.drop(drop_cols, axis=1)

    # Sex has missing values that should be filled with zero
    df = df.fillna(0).replace(9, 0)

    symp_cols = df.columns.drop(cause_col)
    if not ((df[symp_cols] == 1) | (df[symp_cols] == 0)).all().all():
        raise ValueError(f'Non-binary cells in {module} symptoms file')

    return df.groupby(cause_col).mean()


@cli.command(short_help='Calculate endorsement rates.')
@click.pass_context
def endorsements(ctx):
    """Calculate endorsement rates from the validated data."""
    ctx.obj['out_dir'].mkdir(parents=True, exist_ok=True)

    for module in ctx.obj['modules']:
        filepath = ctx.obj['smartva_data'] / f'validated-{module}.csv'
        logging.info(fmt_blue('Loading: ') + str(filepath))

        df = pd.read_csv(filepath).pipe(calc_smartva_endorsement_rates, module)

        outfile = ctx.obj['out_dir'] / f'endorsements-smartva-{module}.csv'
        logging.info(fmt_magenta('Saving: ') + str(outfile))
        df.to_csv(outfile)


if __name__ == '__main__':
    cli()
