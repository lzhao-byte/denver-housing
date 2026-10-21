"""Smoke tests: the Dash app imports and its callbacks run on real data."""

import json

import plotly.graph_objects as go
import pytest
from conftest import run_callback
from dash.exceptions import PreventUpdate


@pytest.fixture(scope="module")
def app():
    import app as app_module

    return app_module


def test_layout_builds(app):
    assert app.app.layout is not None
    assert len(app.app.callback_map) == 16


def test_predict_flow(app):
    args = ['Athmar Park', 3, 2, None, '10 - 20', None, None, None, None, None, None, 5]
    children, table_json, style = run_callback(app.predict_house_price, *args, 1, 1, 0,
                                               triggered='confirm-predict.n_clicks')
    rows = json.loads(table_json)
    assert len(rows) == 2 ** 6 and style == {'display': 'block'}
    assert 'Athmar Park' in children[0].children

    # filter the table by price, then export it
    prices = sorted(r['Predicted Price ($)'] for r in rows)
    kept = run_callback(app.filter_predict_table, prices[10], str(prices[20]), 1, table_json)
    assert len(kept) == 11
    href = run_callback(app.save_predict_table, {'margin-top': 20}, table_json)
    assert href.startswith('data:text/csv') and 'Predicted%20Price' in href


def test_predict_requires_confirmation(app):
    with pytest.raises(PreventUpdate):
        run_callback(app.predict_house_price, 'Athmar Park', *[None] * 11, 1, 0, 0,
                     triggered='button-predict.n_clicks')


def test_history_search_and_house_details(app):
    fig, _, _ = run_callback(app.update_house_map, None, None, None, None, None, None, None, None, None, None,
                             'Athmar Park', None, 1, 1, 0, triggered='confirm-history.n_clicks')
    go.Figure(fig)
    sched = fig['data'][0]['locations'].iloc[0]
    details, layout = run_callback(app.select_from_house_map, {'points': [{'location': sched}]}, 0, 0,
                                   triggered='denver-house-map.selectedData')
    assert layout == 'six columns'
    assert 'Sale Price' in details.children[1].children[1].children[0]


def test_neighborhood_tab(app):
    sel = ['Athmar Park', 'Baker']
    go.Figure(run_callback(app.update_neighbor_map, sel, {}))
    fig, _ = run_callback(app.update_stores_map, sel)
    go.Figure(fig)
    table = run_callback(app.print_neighbor_table, sel, 'Safety')[0]
    assert len(table.data) == 2
    go.Figure(run_callback(app.update_neighbor_price_chart, sel, 'Median Sale Price'))


@pytest.mark.parametrize('metric', [None, 'Median Sale Price', 'Homes Sold', 'Seasonality of Median Price'])
def test_city_tab(app, metric):
    go.Figure(run_callback(app.update_fig_nsc, metric))
    go.Figure(run_callback(app.update_city_fig_ccc, ['Denver, CO', 'Austin, TX'], metric))
