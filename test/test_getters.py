import itertools
import os
import types

import pandas as pd
import pytest

from tariff2.loaders import *


@pytest.mark.parametrize('dataset', ['phmrc', 'nhmrc'])
@pytest.mark.parametrize('module', ['adult', 'child', 'neonate', None])
def test_get_gold_standard(dataset, module):
    gs = get_gold_standard(dataset, module)
    assert isinstance(gs, pd.DataFrame)


@pytest.mark.parametrize('codebook', [
    'odk',
    'presymptom',
    'adult_symptom',
    'child_symptom',
    'neonate_symptom',
])
@pytest.mark.parametrize('suffix', ['', '.csv'])
def test_get_codebook(codebook, suffix):
    cb = get_codebook(''.join([codebook, suffix]))
    assert isinstance(cb, pd.DataFrame)


@pytest.mark.parametrize('src,target', list(itertools.product([
    'gs_code55', 'gs_code46', 'gs_code34',
    'gs_text55', 'gs_text46', 'gs_text34',
    'va55', 'va46', 'va34',
    'smartva', 'smartva_text', 'smartva_reporting',
], repeat=2)))
def test_get_cause_map(module, src, target):
    cause_map = get_cause_map(module, src, target)
    assert cause_map
    assert isinstance(cause_map, dict)


class TestGetMetadata(object):
    def test_single_yml(self, yml_adult_cause_num_to_letter):
        md = get_metadata(yml_adult_cause_num_to_letter)
        expected = {
            'adult': {'cause': {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}},
            'child': {},
            'neonate': {},
        }
        assert md == expected

    def test_single_yml_with_module(self, yml_adult_cause_num_to_letter):
        md = get_metadata(yml_adult_cause_num_to_letter, modules='adult')
        expected = {
            'cause': {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
        }
        assert md == expected

    def test_single_yml_with_two_modules(self, yml_adult_cause_num_to_letter):
        md = get_metadata(yml_adult_cause_num_to_letter,
                          modules=['adult', 'child'])
        expected = {
            'adult': {'cause': {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}},
            'child': {},
        }
        assert md == expected

    def test_single_yml_with_key(self, yml_adult_cause_num_to_letter):
        md = get_metadata(yml_adult_cause_num_to_letter, keys='cause')
        expected = {
            'adult': {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'},
            'child': {},
            'neonate': {}
        }
        assert md == expected

    def test_yml_with_module_and_key(self, yml_adult_cause_num_to_letter):
        md = get_metadata(yml_adult_cause_num_to_letter, modules='adult',
                          keys='cause')
        expected = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
        assert md == expected

    def test_two_yml(self, yml_adult_cause_num_to_letter,
                     yml_child_cause_num_to_letter):
        ymls = [yml_adult_cause_num_to_letter,
                yml_child_cause_num_to_letter]
        md = get_metadata(ymls)
        expected = {
            'adult': {'cause': {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}},
            'child': {'cause': {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}},
            'neonate': {},
        }
        assert md == expected

    def test_two_yml_with_two_modules(self, yml_adult_cause_num_to_letter,
                                      yml_child_cause_num_to_letter):
        ymls = [yml_adult_cause_num_to_letter,
                yml_child_cause_num_to_letter]
        md = get_metadata(ymls, modules=['adult', 'child'])
        expected = {
            'adult': {'cause': {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}},
            'child': {'cause': {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}},
        }
        assert md == expected

    def test_two_yml_with_modules_and_key(self, yml_adult_cause_num_to_letter,
                                          yml_child_cause_num_to_letter):
        ymls = [yml_adult_cause_num_to_letter,
                yml_child_cause_num_to_letter]
        md = get_metadata(ymls, modules=['adult', 'child'], keys='cause')
        expected = {
            'adult': {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'},
            'child': {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'},
        }
        assert md == expected


def test_get_smartva_presymptom_file(tmpdir, module):
    f_name = '{}-presymptom.csv'.format(module)
    f = tmpdir.mkdir('intermediate-files').join(f_name)
    f.write('\n'.join(['sid,q1,q2', '1,1,1', '2,2,2', '']))

    df = get_smartva_presymptom_file(tmpdir.strpath, module)

    assert isinstance(df, pd.DataFrame)
    assert df.index.name == 'sid'
    assert df.index.is_object()


def test_get_smartva_symptom_file(tmpdir, module):
    f_name = '{}-symptom.csv'.format(module)
    f = tmpdir.mkdir('intermediate-files').join(f_name)
    f.write('\n'.join(['sid,q1,q2,age.1', '1,1,1,1', '2,2,2,2', '']))

    df = get_smartva_symptom_file(tmpdir.strpath, module)

    assert isinstance(df, pd.DataFrame)
    assert df.index.name == 'sid'
    assert df.index.is_object()
    assert 'age.1' not in df


def test_get_smartva_ranks_file(tmpdir, module):
    f_name = '{}-tariff-ranks.csv'.format(module)
    f = tmpdir.mkdir('intermediate-files').join(f_name)
    f.write('\n'.join(['sid,1,2,3', '1,1,1,1', '2,2,2,2', '']))

    df = get_smartva_ranks_file(tmpdir.strpath, module)

    assert isinstance(df, pd.DataFrame)
    assert df.index.name == 'sid'
    assert df.index.is_object()
    assert df.columns.is_numeric()


@pytest.fixture
def rank_data(tmpdir, module):
    rows = [['sid', '1', '2', '3'],
            ['s1', '1', '8', '7'],
            ['s2', '1', '7', '8'],
            ['s3', '4', '1', '6'],
            ['s4', '5', '6', '1'],
            []]
    f_name = '{}-tariff-ranks.csv'.format(module)
    f = tmpdir.mkdir('intermediate-files').join(f_name)
    f.write('\n'.join([','.join(row) for row in rows]))
    return f


@pytest.fixture
def symptom_data(tmpdir, module):
    rows = [['sid', 'cause', 's1', 's2'],
            ['s1', '', '0', '0'],
            ['s2', '4', '0', '0'],
            ['s3', '', '1', '0'],
            ['s4', '2', '0', '1'],
            []]
    f_name = '{}-symptom.csv'.format(module)
    f = tmpdir.join('intermediate-files', f_name)
    f.write('\n'.join([','.join(row) for row in rows]))
    return f


class TestGetSmartvaPredictions(object):
    def test_just_prediction(self, tmpdir, module, rank_data):
        pred = get_smartva_predictions(tmpdir.strpath, module, rules=False)
        expected = pd.Series([1, 1, 2, 3], index=['s1', 's2', 's3', 's4'])
        assert (pred == expected).all()

    def test_with_full_map(self, tmpdir, module, rank_data):
        cause_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
        pred = get_smartva_predictions(tmpdir.strpath, module, rules=False,
                                       cause_map=cause_map)
        expected = pd.Series(['A', 'A', 'B', 'C'],
                             index=['s1', 's2', 's3', 's4'])
        assert (pred == expected).all()

    def test_with_partial_map(self, tmpdir, module, rank_data):
        pred = get_smartva_predictions(tmpdir.strpath, module, rules=False,
                                       cause_map={2: 'Two'})
        expected = pd.Series([1, 1, 'Two', 3], index=['s1', 's2', 's3', 's4'])
        assert (pred == expected).all()

    def test_with_rules(self, tmpdir, module, rank_data, symptom_data):
        pred = get_smartva_predictions(tmpdir.strpath, module, rules=True)
        expected = pd.Series([1, 4, 2, 2], index=['s1', 's2', 's3', 's4'])
        assert (pred == expected).all()

    def test_with_rules_and_full_map(self, tmpdir, module, rank_data,
                                     symptom_data):
        cause_map = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
        pred = get_smartva_predictions(tmpdir.strpath, module, rules=True,
                                       cause_map=cause_map)
        expected = pd.Series(['A', 'D', 'B', 'B'],
                             index=['s1', 's2', 's3', 's4'])
        assert (pred == expected).all()

    def test_with_rules_and_partial_map(self, tmpdir, module, rank_data,
                                        symptom_data):
        pred = get_smartva_predictions(tmpdir.strpath, module, rules=True,
                                       cause_map={2: 'Two'})
        expected = pd.Series([1, 4, 'Two', 'Two'],
                             index=['s1', 's2', 's3', 's4'])
        assert (pred == expected).all()


@pytest.mark.parametrize('add_headers', [
    ['age.1'],
    ['cause', 'real_age', 'real_gender'],
    ['real_age', 'real_gender'],
    ['real_age', 'real_gender', 'age.1'],
])
def test_get_smartva_symptoms(tmpdir, module, add_headers):
    f_name = '{}-symptom.csv'.format(module)
    f = tmpdir.mkdir('intermediate-files').join(f_name)

    headers = ['sid', 'q1', 'q2']
    headers.extend(add_headers)
    data1 = ','.join(['1'] * len(headers))
    data2 = ','.join(['2'] * len(headers))
    f.write('\n'.join(['sid,q1,q2', data1, data2, '']))

    df = get_smartva_symptom_file(tmpdir.strpath, module)

    assert isinstance(df, pd.DataFrame)
    assert df.index.name == 'sid'
    assert df.index.is_object()
    for h in add_headers:
        assert h not in df


needs_smartva_repo = pytest.mark.skipif(
    not os.path.exists(pytest.config.getoption("--smartva-repo")),
    reason='Cannot find Smartva repo'
)


@needs_smartva_repo
def test_load_smartva_data(smartva_repo, module):
    data = load_smartva_tariff_data(smartva_repo, module)
    assert isinstance(data, types.ModuleType)
    assert smartva_repo not in sys.path


@needs_smartva_repo
def test_load_smartva_tariff_matrix(smartva_repo, module):
    tariffs = load_smartva_tariff_matrix(smartva_repo, module)
    assert isinstance(tariffs, pd.DataFrame)
    assert tariffs.index.name == 'cause'
    assert tariffs.index.is_numeric()


@needs_smartva_repo
def test_load_smartva_validated_data(smartva_repo, module):
    df = load_smartva_validated_data(smartva_repo, module)
    assert isinstance(df, pd.DataFrame)
    assert df.index.name == 'sid'
    assert df.index.is_object()
