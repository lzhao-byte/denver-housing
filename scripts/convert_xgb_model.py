"""One-off: convert the 2020 XGBoost model from the legacy binary format to UBJSON.

XGBoost 3 can no longer read the legacy binary format, so this has to run under
XGBoost < 3:

    uv run --no-project --with "xgboost<3" --with pandas python scripts/convert_xgb_model.py

The legacy file did not store feature names. The training order below was
recovered from the split thresholds of each feature in the trees, and it is
confirmed by `tests/test_model.py`, which reproduces the notebook's held-out
RMSE with it. Saving the names in the model makes XGBoost reject inputs whose
columns are missing or out of order.
"""

from pathlib import Path

import numpy as np
import xgboost as xgb

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "Models" / "model_xgb_regressor.model"
OUT = ROOT / "Models" / "model_xgb_regressor.ubj"

# Training order: dfx.columns.difference(...) in Part2, with the column names
# used at the time (bathrooms and a few census fields sorted differently).
MODEL_FEATURES = [
    "AGE", "AREA_ABG", "AVG_HH_INC", "BACHELORSO", "BED_RMS", "CCAGE_RM",
    "CCYRBLT", "Colleges", "Crimes", "DrugDist", "FBSMT_SQFT", "FoodStores",
    "GRD_AREA", "BATH_RMS", "Intersects", "K12s", "LAND_SQFT", "LESSTHANHS",
    "Libraries", "Malls", "Marijuana", "MaxPctRace", "MaxRaceTyp_BLACK",
    "MaxRaceTyp_HISPAN", "MaxRaceTyp_WHITE", "PCT_AGE65P", "PCT_AGELES",
    "PER_CAPITA", "PCT_SOLD", "PCT_VAC", "PER_COMM", "ParkDist",
    "Park_Coverage", "SALE_MONTH", "SALE_YEAR", "STORY", "StLights",
    "StoreDist", "TrAccident", "Tree_Coverage",
]


def main():
    legacy = xgb.Booster()
    legacy.load_model(str(LEGACY))
    assert legacy.num_features() == len(MODEL_FEATURES)

    converted = xgb.Booster(model_file=str(LEGACY))
    converted.feature_names = MODEL_FEATURES
    converted.feature_types = ["float"] * len(MODEL_FEATURES)
    converted.save_model(str(OUT))

    # Same trees, so predictions must match exactly.
    x = np.random.default_rng(0).uniform(0, 5000, size=(1000, len(MODEL_FEATURES)))
    reloaded = xgb.Booster(model_file=str(OUT))
    before = legacy.predict(xgb.DMatrix(x))
    after = reloaded.predict(xgb.DMatrix(x, feature_names=MODEL_FEATURES))
    np.testing.assert_array_equal(before, after)
    print(f"wrote {OUT.relative_to(ROOT)}; predictions identical on {len(x)} rows")


if __name__ == "__main__":
    main()
