import pandas as pd
import pytest

from scripts.build_model_inputs import COLUMNS, build


def test_takes_latest_year_one_row_per_neighborhood():
    records = pd.DataFrame({
        'NBHD_ID': [1, 1, 1, 2],
        'SALE_YEAR': [2018, 2019, 2019, 2019],
        'PCT_SOLD': [0.01, 0.03, 0.03, 0.05],
        'MaxRaceTyp_BLACK': [0, 0, 0, 1],
        'MaxRaceTyp_HISPAN': [1, 1, 1, 0],
        'MaxRaceTyp_WHITE': [0, 0, 0, 0],
    })
    out = build(records)
    assert out['NBHD_ID'].tolist() == [1, 2]
    assert out['PCT_SOLD'].tolist() == [0.03, 0.05]


def test_committed_csv_matches_training_data(records):
    committed = pd.read_csv('CSVFiles/NeighborModelInputs.csv')
    pd.testing.assert_frame_equal(committed, build(records), check_dtype=False)
    assert (committed[['MaxRaceTyp_BLACK', 'MaxRaceTyp_HISPAN', 'MaxRaceTyp_WHITE']].sum(axis=1) == 1).all()
    assert committed['PCT_SOLD'].between(0, 1).all()


@pytest.mark.parametrize('col', COLUMNS)
def test_columns_are_constant_within_neighborhood_year(records, col):
    assert records.groupby(['NBHD_ID', 'SALE_YEAR'])[col].nunique().max() == 1
