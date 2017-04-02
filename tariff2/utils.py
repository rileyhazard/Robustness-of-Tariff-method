from functools import reduce
import operator

import numpy as np
import pandas as pd
from sklearn.utils.validation import check_consistent_length, column_or_1d


def union_NDFrame_indicies(*frames, sort=False):
    """Return the subset of indices common to all frames.

    Rows with non-matching indicies are dropped. If the rows are not sorted,
    they will be returned in an arbitary order. However, all the indicies
    of all the frames will be in the same order. None NDFrames are removed.

    Args:
        *frames: pandas series or dataframes
        sorted: should the indicies be sorted

    Returns:
        (list of frames)

    Warning:
        This will only keep the first instances of duplicated indicies.
    """
    frames = [f for f in frames if isinstance(f, pd.core.generic.NDFrame)]
    union = list(reduce(operator.and_, [set(f.index) for f in frames]))
    if sort:
        union = sorted(union)
    return [f.loc[union] for f in frames]


def safe_align_sequences(*seqs):
    """Align sequences accounting for pandas indicies.

    If pandas.NDFrames are passed, they are unioned and non-matching
    observations are dropped. If some NDFrames and some non-NDFrames are
    passed, it is assumed the order is consistent across all sequences.

    Args:
        seqs (sequence of sequences)

    Returns:
        tuple of np.arrays
    """
    if all([isinstance(s, pd.core.generic.NDFrame) for s in seqs]):
        seqs = union_NDFrame_indicies(*seqs)

    check_consistent_length(*seqs)
    return [column_or_1d(s) for s in seqs]


def is_uncertain(arr, ui=(2.5, 97.5)):
    """Returns True if the uncertainty interval of the array contains zero

    Args:
        arr (sequence): sequence of values
        ui (tuple of 2 floats): lower and upper bounds of uncertainty interval
            between 0 and 100

    Returns:
        (bool)
    """
    lower, upper = np.percentile(arr, ui)
    return lower < 0 and upper > 0


def calc_ui(arr, ui=(2.5, 97.5), labels=None):
    """Calculate the uncertainty interval around a sequence of values.

    Args:
        arr (sequence): sequence of values
        ui (tuple of 2 floats): lower and upper bounds of uncertainty interval
            between 0 and 100
        labels=(tuple of 2 str): return a pandas.Series with index values set
            to the labels

    Returns:
        ui (np.array or pd.Series)

    """
    ui = np.percentile(arr, ui)
    if labels:
        ui = pd.Series(ui, index=labels)
    return ui


def make_mask(matrix, rows, cols, ignore_errors=True):
    """Transform dict of list matrix into a boolean numpy array.

    The dict keys are assumed to be column labels and the list values
    are assumed to be row labels.

    Args:
        matrix (dict of lists): sparse-ish matrix
        rows (sequence): row labels
        cols (sequence): column labels
        errors (str): Ignore index errors if there are values in the matrix
            which are not in the rows or columns.

    Returns:
        mask (np.array): 2D boolean array where values in matrix are True

    """
    n_rows = len(rows)
    n_cols = len(cols)
    if len(set(rows)) != n_rows:
        raise ValueError('Duplicate row labels.')
    if len(set(cols)) != n_cols:
        raise ValueError('Duplicate column labels')

    arr = np.full((n_rows, n_cols), False, dtype=bool)
    for col, row_vals in matrix.items():
        if ignore_errors and col not in cols:
            continue
        col_idx = np.where(cols == col)[0][0]
        for row in row_vals:
            if ignore_errors and row not in rows:
                continue
            row_idx = np.where(rows == row)[0][0]
            arr[row_idx, col_idx] = True

    return arr
