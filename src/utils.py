from functools import reduce
import operator

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
