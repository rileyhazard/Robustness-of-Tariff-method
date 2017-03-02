import pytest
import sklearn.utils.estimator_checks as checks

from src.tariff import TariffClassifier


NAME = 'TariffClassifier'
CLF = TariffClassifier


def test_parameters_default_constructible():
    checks.check_parameters_default_constructible(NAME, CLF)


#######################
#   Non-meta-checks   #
#######################

def test_estimators_dtypes():
    checks.check_estimators_dtypes(NAME, CLF)


def test_fit_score_takes_y():
    checks.check_fit_score_takes_y(NAME, CLF)


def test_dtype_object():
    checks.check_dtype_object(NAME, CLF)


def test_sample_weights_pandas_series():
    checks.check_sample_weights_pandas_series(NAME, CLF)


def test_sample_weights_list():
    checks.check_sample_weights_list(NAME, CLF)


def test_estimators_fit_returns_self():
    checks.check_estimators_fit_returns_self(NAME, CLF)


def test_pipeline_consistency():
    checks.check_pipeline_consistency(NAME, CLF)


def test_estimators_nan_inf():
    checks.check_estimators_nan_inf(NAME, CLF)


def test_estimators_overwrite_params():
    checks.check_estimators_overwrite_params(NAME, CLF)


def test_estimator_sparse_data():
    checks.check_estimator_sparse_data(NAME, CLF)


def test_estimators_pickle():
    checks.check_estimators_pickle(NAME, CLF)


#########################
#   Classifier Checks   #
#########################

def test_classifier_data_not_an_array():
    checks.check_classifier_data_not_an_array(NAME, CLF)


def test_classifiers_one_label():
    checks.check_classifiers_one_label(NAME, CLF)


def test_classifiers_classes():
    checks.check_classifiers_classes(NAME, CLF)


def test_estimators_partial_fit_n_features():
    checks.check_estimators_partial_fit_n_features(NAME, CLF)


def test_classifiers_train():
    checks.check_classifiers_train(NAME, CLF)


def test_classifiers_regression_target():
    checks.check_classifiers_regression_target(NAME, CLF)


def test_supervised_y_2d():
    checks.check_supervised_y_2d(NAME, CLF)


def test_estimators_unfitted():
    checks.check_estimators_unfitted(NAME, CLF)


def test_class_weight_classifiers():
    checks.check_class_weight_classifiers(NAME, CLF)


def test_non_transformer_estimators_n_iter():
    checks.check_non_transformer_estimators_n_iter(NAME, CLF)


#########################
#   Other Base Checks   #
#########################

def test_fit2d_predict1d():
    checks.check_fit2d_predict1d(NAME, CLF)


def test_fit2d_1sample():
    checks.check_fit2d_1sample(NAME, CLF)


def test_fit2d_1feature():
    checks.check_fit2d_1feature(NAME, CLF)


def test_fit1d_1feature():
    checks.check_fit1d_1feature(NAME, CLF)


def test_fit1d_1sample():
    checks.check_fit1d_1sample(NAME, CLF)


def test_get_params_invariance():
    checks.check_get_params_invariance(NAME, CLF)


def test_dict_unchanged():
    checks.check_dict_unchanged(NAME, CLF)


@pytest.mark.skip(reason='Wrong version')
def test_no_fit_attributes_set_in_init():
    checks.check_no_fit_attributes_set_in_init(NAME, CLF)


@pytest.mark.skip(reason='Wrong version')
def test_dont_overwrite_parameters():
    checks.check_dont_overwrite_parameters(NAME, CLF)
