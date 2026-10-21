"""family_demo_filter: the sales-history search."""

import pandas as pd
import pytest

import utils

HOUSES = pd.DataFrame({
    'SALE_PRICE': [300_000, 450_000, 900_000, 450_000],
    'SALE_YEAR': [2012, 2015, 2018, 2015],
    'BED_RMS': [2, 3, 3, 3],
    'AREA_ABG': [2000, 2500, 3000, 2500],
    'LAND_SQFT': [5000, 7000, 12000, 7000],
    'NBRHD_NAME': ['Athmar Park', 'Athmar Park', 'Athmar Park', 'Baker'],
    'STORY': [1, 1, 1, 1],
})
GEOJSON = {'features': [{'properties': {'NBRHD_NAME': n}} for n in ['Athmar Park', 'Baker', 'Athmar Park']]}


def search(maxlot=None, **kw):
    args = dict(min_price=None, max_price=None, min_year=None, max_year=None, min_bed=None, max_bed=None,
                minarea=None, maxarea=None, minlot=None, maxlot=maxlot, neighbor=None, story=None)
    args.update(kw)
    return utils.family_demo_filter(*args.values(), HOUSES, GEOJSON)


def test_blank_max_lot_uses_default_instead_of_returning_nothing():
    # Regression: a blank Max lot used to compare LAND_SQFT <= None, which matched no rows.
    _, houses = search(maxlot=None)
    assert houses['LAND_SQFT'].tolist() == [5000, 7000]


def test_bounds_are_inclusive():
    _, houses = search(min_price=450_000, max_price=900_000, maxlot=12_000)
    assert houses['SALE_PRICE'].tolist() == [450_000, 900_000]


@pytest.mark.parametrize('neighbor, n_houses, n_shapes', [(None, 2, 2), ('Baker', 1, 1)])
def test_filters_to_one_neighborhood(neighbor, n_houses, n_shapes):
    shapes, houses = search(neighbor=neighbor)
    assert len(houses) == n_houses
    assert len(shapes['features']) == n_shapes
