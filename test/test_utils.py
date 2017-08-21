import numpy as np
import pandas as pd
import pytest

from src.utils import *


@pytest.mark.parametrize('frames', [
    ([pd.Series(np.ones(3), index=[1, 3, 5])]),

    ([pd.DataFrame(np.ones((3, 3)), index=[1, 3, 5])]),

    ([pd.Series(np.ones(3), index=[1, 3, 5]),
      pd.DataFrame(np.ones((5, 3)), index=[1, 2, 3, 4, 5])]),

    ([pd.Series(np.ones(5), index=[1, 2, 3, 4, 5]),
      pd.DataFrame(np.ones((3, 3)), index=[1, 3, 5]),
      pd.DataFrame(np.ones((4, 3)), index=[1, 3, 5, 9])]),

    ([pd.Series(np.ones(5), index=[3, 2, 1, 4, 5]),
      pd.DataFrame(np.ones((3, 3)), index=[5, 1, 3]),
      pd.DataFrame(np.ones((4, 3)), index=[9, 5, 3, 1])]),

    ([pd.Series(np.ones(3), index=[1, 3, 5]),
      pd.DataFrame(np.ones((3, 3)), index=[1, 3, 5]),
      np.array([1, 3, 5])]),
])
def test_union_NDFrame_indicies(frames):
    unioned = union_NDFrame_indicies(*frames, sort=True)
    idx = np.array([1, 3, 5])
    assert all([(frame.index == idx).all() for frame in unioned])


@pytest.mark.parametrize('seqs', [
    ([(1, 2, 3), [1, 2, 3]]),
    ([(1, 2, 3), np.array([1, 2, 3])]),
    ([pd.Series([1, 2, 3]), pd.Series([4, 5, 6])]),
    ([pd.Series([1, 2, 3]), np.arange(3)]),
    ([pd.Series([1, 2, 3], index=['a', 'b', 'c']),
      pd.Series([4, 5, 6], index=['a', 'b', 'c'])]),
    ([pd.Series([1, 2, 3], index=['a', 'b', 'c']),
      pd.Series([4, 5, 6], index=['c', 'a', 'b'])]),
])
def test_safe_align_sequences(seqs):
    aligned = safe_align_sequences(*seqs)
    assert all([isinstance(seq, np.ndarray) for seq in aligned])
    shapes = np.unique([seq.shape for seq in aligned])
    assert len(shapes) == 1
    assert int(shapes[0])  # only one dimension


def test_make_mask():
  np.sum(mask) == sum([len(v) for k, v in matrix.items()])