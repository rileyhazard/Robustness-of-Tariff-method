import inspect
import os

import pandas as pd
import pytest

from src.rules.rule import Rule
from src.rules.specification import RULES_FOR_DOC, RULES_BY_MODULE


MODULES = ['adult', 'child', 'neonate']
CODEBOOK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            '..', '..', 'codebooks')

RULES_AND_MODULE = []
for module, rule_list in RULES_BY_MODULE.items():
    RULES_AND_MODULE.extend(zip(rule_list, [module] * len(rule_list)))


@pytest.fixture(scope='module')
def causes():
    cause_map = pd.read_csv(os.path.join(CODEBOOK_DIR, 'cause_map.csv'))

    all_causes = set(cause_map.gs_text46).union(cause_map.gs_text34)

    by_module = {}
    for module in MODULES:
        mod = cause_map.loc[cause_map.module == module]
        by_module[module] = set(mod.gs_text46).union(mod.gs_text34)

    return all_causes, by_module


def test_all_rules_in_doc():
    assert set(RULES_FOR_DOC) == set([fn for fn, module in RULES_AND_MODULE])


@pytest.fixture(scope='module')
def presymptom():
    presymptom = pd.read_csv(os.path.join(CODEBOOK_DIR, 'presymptom.csv'))
    return set(presymptom.variable)


@pytest.mark.parametrize('fn', RULES_FOR_DOC, ids=lambda x: x.__name__)
def test_returns_boolean_for_doc(fn):
    args, _, _, _ = inspect.getargspec(fn)
    assert isinstance(fn(*[0 for arg in args]), bool)


@pytest.mark.parametrize('fn, module', RULES_AND_MODULE,
                         ids=lambda x: x.__name__)
def test_returns_boolean_by_module(fn, module):
    args, _, _, _ = inspect.getargspec(fn)
    assert isinstance(fn(*[0 for arg in args]), bool)


@pytest.mark.parametrize('fn', RULES_FOR_DOC, ids=lambda x: x.__name__)
def test_rule_has_valid_module(fn):
    rule_ = Rule(fn)
    assert rule_.module
    if isinstance(rule_.module, basestring):
        assert rule_.module in MODULES
    else:
        assert set(rule_.module).issubset(MODULES)


@pytest.mark.parametrize('fn, module', RULES_AND_MODULE,
                         ids=lambda x: x.__name__)
def test_rule_has_specified_module(fn, module):
    rule_ = Rule(fn)
    assert rule_.module
    if isinstance(rule_.module, basestring):
        assert rule_.module == module
    else:
        assert module in rule_.module


@pytest.mark.parametrize('fn', RULES_FOR_DOC, ids=lambda x: x.__name__)
def test_has_valid_prediction(fn, causes):
    all_causes, causes_by_module = causes
    rule_ = Rule(fn)
    assert rule_.prediction
    if isinstance(rule_.prediction, basestring):
        assert rule_.prediction in all_causes
    else:
        assert set(rule_.prediction).issubset(all_causes)


@pytest.mark.parametrize('fn, module', RULES_AND_MODULE,
                         ids=lambda x: x.__name__)
def test_has_specified_prediction(fn, module, causes):
    all_causes, causes_by_module = causes
    rule_ = Rule(fn)
    assert rule_.prediction
    if isinstance(rule_.prediction, basestring):
        assert rule_.prediction in causes_by_module[module]
    else:
        module_prediction = rule_.prediction[rule_.module.index(module)]
        assert module_prediction in causes_by_module[module]


@pytest.mark.parametrize('fn', RULES_FOR_DOC, ids=lambda x: x.__name__)
def test_has_valid_questions(fn, presymptom):
    rule_ = Rule(fn)
    assert rule_.questions
    if isinstance(rule_.module, basestring):
        questions_list = [rule_.questions]
    else:
        questions_list = rule_.questions

    for questions in questions_list:
        non_words_questions = [question for question in questions
                               if not question.startswith('s9999')]
        assert set(questions).issubset(non_words_questions)


@pytest.mark.parametrize('fn', RULES_FOR_DOC, ids=lambda x: x.__name__)
def test_questions_match_params(fn):
    rule_ = Rule(fn)
    assert rule_.questions
    if isinstance(rule_.module, basestring):
        questions_list = [rule_.questions]
    else:
        questions_list = rule_.questions

    args, _, _, defaults = inspect.getargspec(fn)
    if defaults:
        n_required = len(args) - len(defaults)
    else:
        n_required = len(args)
    for questions in questions_list:
        assert len(questions) >= n_required
        for arg in args[:n_required]:
            assert arg in questions


@pytest.mark.parametrize('fn', RULES_FOR_DOC, ids=lambda x: x.__name__)
def test_parse_conditions(fn):
    rule_ = Rule(fn)
    assert rule_.conditions
    assert all([isinstance(c, basestring) for c in rule_.conditions])


@pytest.mark.parametrize('fn', RULES_FOR_DOC, ids=lambda x: x.__name__)
def test_parse_notes(fn):
    rule_ = Rule(fn)
    if 'Note:' in fn.__doc__:
        assert isinstance(rule_.notes, basestring)


@pytest.mark.parametrize('fn', RULES_FOR_DOC, ids=lambda x: x.__name__)
def test_parse_footnotes(fn):
    rule_ = Rule(fn)
    if '*' in fn.__doc__:
        assert isinstance(rule_.footnotes, basestring)


@pytest.mark.parametrize('fn', RULES_FOR_DOC, ids=lambda x: x.__name__)
def test_parse_cases(fn):
    rule_ = Rule(fn)
    assert rule_.cases
    assert all([isinstance(c, basestring) for c in rule_.conditions])


@pytest.mark.parametrize('fn, module', RULES_AND_MODULE,
                         ids=lambda x: x.__name__)
def test_get_questions(fn, module):
    rule_ = Rule(fn)
    questions = rule_.get_questions(module)
    assert isinstance(questions, dict)
