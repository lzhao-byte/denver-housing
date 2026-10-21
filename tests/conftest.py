import os
import sys
from contextvars import copy_context
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
# The app reads its data with paths relative to the repo root.
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def files():
    """Everything load_files() returns, keyed by name (loads ~90MB of data once)."""
    import utils

    names = ["json_neighbor", "neighbor_prices", "json_single_family", "neighbor_house_record", "metrics",
             "cities", "city_data", "family_dist", "family_demo", "city_seasonality", "neighbor_demo",
             "neighbor_stats", "nbhd_stats", "sectors", "cpi"]
    return dict(zip(names, utils.load_files()))


@pytest.fixture(scope="session")
def records():
    """Cleaned training records from Notebooks/Part2."""
    return pd.read_csv(ROOT / "Data" / "cleaned_house_records.csv")


def run_callback(fn, *args, triggered=""):
    """Call a Dash callback outside a request, with `triggered` as the input that fired it."""
    from dash._callback_context import context_value
    from dash._utils import AttributeDict

    def run():
        context_value.set(AttributeDict(triggered_inputs=[{"prop_id": triggered, "value": 1}] if triggered else []))
        return fn(*args)

    return copy_context().run(run)
