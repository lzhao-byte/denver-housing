"""predict_house_xgb: builds the model inputs the way training did."""

import numpy as np
import pandas as pd
import pytest
import xgboost as xgb

import utils

TABLE_COLUMNS = ['Story', 'Bedrooms', 'Bathrooms', 'Age of House (yrs)', 'Above Ground Area (sqft)',
                 'Lot Size (sqft)', 'Distance to Park (meters)', 'Distance to Food Stores (meters)',
                 'Predicted Price ($)']


def predict(files, neighbor=None, bed=None, bath=None, story=None, age=None, minarea=None, maxarea=None,
            minlot=None, maxlot=None, park=None, store=None, month=None):
    return utils.predict_house_xgb(neighbor, bed, bath, story, age, minarea, maxarea, minlot, maxlot, park, store,
                                   month, files["neighbor_stats"], files["neighbor_demo"], files["cpi"])


@pytest.fixture
def captured_inputs(monkeypatch):
    """Record the DataFrame handed to the model."""
    seen = []
    real = xgb.DMatrix

    def spy(data, *args, **kwargs):
        seen.append(data.copy())
        return real(data, *args, **kwargs)

    monkeypatch.setattr(utils.xgb, "DMatrix", spy)
    return seen


def test_defaults_give_full_grid_of_positive_prices(files):
    table = predict(files)
    assert list(table.columns) == TABLE_COLUMNS
    # 2 beds x 2 baths x 2 stories x 2 ages x 2 areas x 2 lots x 2 park x 2 store distances
    assert len(table) == 2 ** 8
    prices = table['Predicted Price ($)']
    assert np.isfinite(prices).all() and (prices > 50_000).all()


def test_selected_values_are_used(files):
    table = predict(files, neighbor='South Park Hill', bed=4, bath=3, story=2, age='20 - 50', park=250, store=1500)
    assert set(table['Bedrooms']) == {4}
    assert set(table['Bathrooms']) == {3}
    assert set(table['Story']) == {2}
    assert set(table['Age of House (yrs)']) == {20, 50}
    assert set(table['Distance to Park (meters)']) == {250}
    assert set(table['Distance to Food Stores (meters)']) == {1500}


def test_bigger_houses_predict_higher_on_average(files):
    table = predict(files, neighbor='South Park Hill', minarea=1200, maxarea=3600)
    by_area = table.groupby('Above Ground Area (sqft)')['Predicted Price ($)'].mean()
    assert by_area[3600] > by_area[1200]


def test_model_inputs_match_training_units(files, captured_inputs, records):
    predict(files, neighbor='Athmar Park', age='10 - 20')
    x = captured_inputs[-1]
    assert list(x.columns) == utils.MODEL_FEATURES

    # neighborhood-level features equal the training data's latest-year values
    nbhd_id = files["neighbor_demo"].set_index('NBHD_NAME').loc['Athmar Park', 'NBHD_ID']
    train = records[(records['NBHD_ID'] == nbhd_id) & (records['SALE_YEAR'] == 2019)].iloc[0]
    for col in ['AVG_HH_INC', 'PER_CAPITA', 'Crimes', 'TrAccident', 'PCT_SOLD', 'MaxRaceTyp_HISPAN']:
        assert x[col].iloc[0] == pytest.approx(train[col]), col
    # coverage is a share of neighborhood area, not square meters
    assert x['Park_Coverage'].iloc[0] == pytest.approx(train['Park_Coverage'], abs=1e-4)
    assert x['Tree_Coverage'].iloc[0] == pytest.approx(train['Tree_Coverage'], abs=1e-4)

    assert (x['CCYRBLT'] == x['SALE_YEAR'] - x['AGE']).all()
    assert (x['CCAGE_RM'] == 0).all() and (x['FBSMT_SQFT'] == 0).all()


def test_cpi_converts_to_nominal_dollars(files, captured_inputs):
    table = predict(files, month=1)
    raw = utils.load_xgb_model().predict(xgb.DMatrix(captured_inputs[-1]))
    cpi_jan = files["cpi"].set_index('month').loc[1, 'cpi']
    np.testing.assert_allclose(table['Predicted Price ($)'], np.round(raw * cpi_jan / 100))


def test_every_dropdown_neighborhood_has_model_inputs(files):
    names = files["neighbor_prices"]['NBHD_NAME'].unique()
    ids = files["neighbor_demo"].set_index('NBHD_NAME').loc[names, 'NBHD_ID']
    assert set(ids) <= set(utils.load_model_inputs().index)
    assert isinstance(predict(files, neighbor=names[-1]), pd.DataFrame)
