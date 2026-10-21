"""Map figures must use trace types and attributes the bundled plotly.js supports.

plotly.js 3 removed the *mapbox traces; dict figures with unknown types or
attributes render blank without an error, so validate them with plotly here.
"""

import pandas as pd
import plotly.graph_objects as go
import pytest

import utils


@pytest.fixture(scope="module")
def figures(files):
    f = files
    features, parks = utils.load_neighbor_features()
    centers = pd.read_csv('CSVFiles/NeighborhoodCenters.csv')
    shapes, houses = utils.family_demo_filter(None, None, 2000, 2019, None, 5, 500, None, 500, None, 'Athmar Park',
                                              None, f["family_demo"], f["json_single_family"])
    return {
        'family_base': utils.draw_family_base_map(f["json_single_family"], f["family_demo"].head(20),
                                                  f["family_dist"].head(20)),
        'neighborhoods': utils.draw_base_map(f["json_neighbor"], f["neighbor_prices"], f["neighbor_house_record"],
                                             ['Athmar Park']),
        'house_search': utils.update_house_base_map(shapes, houses, f["json_neighbor"], f["neighbor_house_record"],
                                                    'Athmar Park'),
        'house_origin': utils.update_house_base_map_origin('Athmar Park', f["json_neighbor"],
                                                           f["neighbor_house_record"]),
        'house_base': utils.draw_house_base_map(f["json_neighbor"], f["neighbor_house_record"]),
        'stores': utils.draw_store_map(['Athmar Park', 'Baker'], features, parks, f["json_neighbor"], centers),
    }


@pytest.mark.parametrize('name', ['family_base', 'neighborhoods', 'house_search', 'house_origin', 'house_base',
                                  'stores'])
def test_map_figure_is_valid_and_token_free(figures, name):
    fig = go.Figure(figures[name])  # raises on unknown trace types or attributes
    assert {t.type for t in fig.data} <= {'choroplethmap', 'scattermap'}
    assert fig.layout.map.style == 'carto-positron'
    assert 'mapbox' not in figures[name]['layout']


def test_house_search_map_has_houses(figures):
    assert len(figures['house_search']['data'][0]['locations']) > 0


def test_store_map_has_a_trace_per_point_type(figures):
    names = [t['name'] for t in figures['stores']['data']]
    assert len(names) == len(set(names)) > 1
    assert all(isinstance(t['marker'], dict) for t in figures['stores']['data'])
