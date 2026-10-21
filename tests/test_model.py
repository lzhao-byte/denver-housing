"""The shipped model and feature order reproduce the notebook's held-out results."""

import numpy as np
import pytest
import xgboost as xgb
from sklearn.metrics import mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import train_test_split

import utils

# Part2_Model_Selection_Tuning.ipynb, tuned XGBoost cell output
NOTEBOOK_RMSE = 44111.87
NOTEBOOK_MEDAE = 13331.98
NOTEBOOK_R2 = 0.89

# The 33 columns the app used to pass by position before the fix
OLD_APP_COLUMNS = ['AGE', 'AREA_ABG', 'AVG_HH_INC', 'BACHELORSO', 'BED_RMS', 'Colleges', 'Crimes', 'DrugDist',
                   'FoodStores', 'GRD_AREA', 'BATH_RMS', 'Intersects', 'K12s', 'LAND_SQFT', 'LESSTHANHS',
                   'Libraries', 'Malls', 'Marijuana', 'MaxPctRace', 'PCT_AGE65P', 'PCT_AGELES', 'PER_CAPITA',
                   'PCT_VAC', 'PER_COMM', 'ParkDist', 'Park_Coverage', 'SALE_MONTH', 'SALE_YEAR', 'STORY',
                   'StLights', 'StoreDist', 'TrAccident', 'Tree_Coverage']


@pytest.fixture(scope="module")
def test_split(records):
    # Same split as the notebook: 25% test, random_state=42, stratified by neighborhood
    _, x_test, _, y_test = train_test_split(records, records["SALE_PRICE_CPI_ADJ"], test_size=0.25,
                                            random_state=42, stratify=records["NBHD_ID"])
    return x_test, y_test.to_numpy()


def test_model_stores_feature_names_in_training_order():
    model = utils.load_xgb_model()
    assert model.feature_names == utils.MODEL_FEATURES
    assert model.num_features() == 40


def test_model_reproduces_notebook_test_metrics(test_split):
    x_test, y_test = test_split
    y_pred = utils.load_xgb_model().predict(xgb.DMatrix(x_test[utils.MODEL_FEATURES]))

    assert np.sqrt(mean_squared_error(y_test, y_pred)) == pytest.approx(NOTEBOOK_RMSE, rel=0.001)
    assert median_absolute_error(y_test, y_pred) == pytest.approx(NOTEBOOK_MEDAE, rel=0.001)
    assert round(r2_score(y_test, y_pred), 2) == NOTEBOOK_R2


def test_old_positional_inputs_were_far_off(test_split):
    """Documents the bug: 33 columns by position, the rest missing, gave R^2 near 0."""
    x_test, y_test = test_split
    x_old = np.full((len(x_test), 40), np.nan)
    x_old[:, :33] = x_test[OLD_APP_COLUMNS].to_numpy()
    y_pred = utils.load_xgb_model().predict(xgb.DMatrix(x_old, feature_names=utils.MODEL_FEATURES))
    assert r2_score(y_test, y_pred) < 0.2


def test_model_rejects_unnamed_or_reordered_columns(test_split):
    x_test, _ = test_split
    model = utils.load_xgb_model()
    with pytest.raises(ValueError):
        model.predict(xgb.DMatrix(x_test[utils.MODEL_FEATURES].to_numpy()))
    with pytest.raises(ValueError):
        model.predict(xgb.DMatrix(x_test[list(reversed(utils.MODEL_FEATURES))]))
