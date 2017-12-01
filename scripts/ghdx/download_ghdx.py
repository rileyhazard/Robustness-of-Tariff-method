
from functools import partial
import logging
from pathlib import Path

import click
import pandas as pd


MODULES = ('adult', 'child', 'neonate')
GHDX_URL = ('http://ghdx.healthdata.org/sites/default/files/'
            'record-attached-files')
REPO = Path(__file__).parent.parent.parent
OUT_DIR = REPO / 'data/ghdx/raw'

fmt_blue = partial(click.style, bold=True, fg='blue')
fmt_magenta = partial(click.style, bold=True, fg='magenta')


def download_phmrc_codebook():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    filename = 'IHME_PHMRC_VA_DATA_CODEBOOK_Y2013M09D11_0'
    url = f'{GHDX_URL}/{filename}.xlsx'
    logging.info(fmt_blue('Downloading: ') + url)
    df = pd.read_excel(url, encoding='latin-1')

    filepath = OUT_DIR / f'{filename}.csv'
    df.to_csv(filepath, encoding='utf-8', index=False)
    logging.info(fmt_magenta('File saved: ') + str(filepath))


def download_phmrc_module(module):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    MODULE = module.upper()
    i = 2 if module == 'child' else 1
    filename = f'IHME_PHMRC_VA_DATA_{MODULE}_Y2013M09D11_{i}'
    url = f'{GHDX_URL}/{filename}.dta'
    logging.info(fmt_blue('Downloading: ') + url)
    df = pd.read_stata(url, encoding='latin-1', convert_categoricals=False)

    filepath = OUT_DIR / f'{filename}.csv'
    df.to_csv(filepath, encoding='utf-8', index=False)
    logging.info(fmt_magenta('File saved: ') + str(filepath))


@click.group(chain=True, invoke_without_command=True)
@click.option('-q', '--quiet', is_flag=True, help='Suppress messages.')
@click.pass_context
def main(ctx, quiet):
    """Download PHMRC data files from the GHDx.

    Commands can be chained. If no files are specified, all will be downloaded.
    """
    if not quiet:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    if ctx.invoked_subcommand is None:
        download_phmrc_codebook()
        for module in MODULES:
            download_phmrc_module(module)


@main.command()
def codebook():
    """Download the codebook."""
    download_phmrc_codebook()


@main.command()
def adult():
    """Download the adult data module."""
    download_phmrc_module('adult')


@main.command()
def child():
    """Download the child data module."""
    download_phmrc_module('child')


@main.command()
def neonate():
    """Download the neonate data module."""
    download_phmrc_module('neonate')


if __name__ == '__main__':
    main()
