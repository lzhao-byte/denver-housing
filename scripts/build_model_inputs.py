"""Build CSVFiles/NeighborModelInputs.csv: neighborhood-level model features the
app's other CSVs don't carry (share of homes sold, majority race one-hots).

Values come from the latest sale year in the training data, matching the
2019-era neighborhood stats the app already uses.

    uv run python scripts/build_model_inputs.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ["PCT_SOLD", "MaxRaceTyp_BLACK", "MaxRaceTyp_HISPAN", "MaxRaceTyp_WHITE"]


def build(records: pd.DataFrame) -> pd.DataFrame:
    latest = records[records["SALE_YEAR"] == records["SALE_YEAR"].max()]
    # These columns are constant within a neighborhood-year.
    return latest.groupby("NBHD_ID")[COLUMNS].first().reset_index()


def main():
    records = pd.read_csv(ROOT / "Data" / "cleaned_house_records.csv")
    out = ROOT / "CSVFiles" / "NeighborModelInputs.csv"
    build(records).to_csv(out, index=False)
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
