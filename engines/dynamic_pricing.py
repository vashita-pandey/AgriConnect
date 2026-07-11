"""
dynamic_pricing.py
====================
Perishability-aware markdown pricing — the core commercial problem in a produce
marketplace that generic e-commerce pricing ignores: unsold inventory doesn't
just sit, it actively loses value as it approaches its shelf-life limit.

Markdown formula (transparent, not a black box):

    markdown_pct = base_decay(age_ratio) * demand_adjustment(crop)

- base_decay: a convex markdown curve — negligible markdown in the first half
  of shelf life, ramping steeply as inventory nears expiry (the same shape used
  in retail perishable-goods markdown literature, e.g. supermarket "reduced to
  clear" stickers).
- demand_adjustment: scales markdown up when demand_forecast.py's 14-day demand
  forecast for that crop is below its recent average (move stock faster), and
  scales it down (or allows a small premium) when forecasted demand is above
  average.
"""

import pandas as pd
import numpy as np
from pathlib import Path

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def base_decay(age_ratio: np.ndarray, max_markdown: float = 0.45) -> np.ndarray:
    """
    age_ratio = days_since_harvest / shelf_life_days, clipped to [0, 1].
    Convex ramp: markdown = max_markdown * age_ratio^3, roughly matching
    retail "reduced to clear" curves that discount lightly at first and
    steeply near expiry.
    """
    age_ratio = np.clip(age_ratio, 0, 1)
    return max_markdown * (age_ratio ** 3)


def demand_adjustment(crop: str, demand_summary: pd.DataFrame) -> float:
    """
    >1.0 = push markdown harder (weak forecasted demand), <1.0 = ease off
    (strong forecasted demand); derived from demand_forecast.py's output.
    """
    row = demand_summary[demand_summary["crop"] == crop]
    if row.empty or pd.isna(row["forecast_daily_demand_kg"].values[0]):
        return 1.0
    forecast = row["forecast_daily_demand_kg"].values[0]
    crop_median = demand_summary["forecast_daily_demand_kg"].median()
    if crop_median == 0 or pd.isna(crop_median):
        return 1.0
    ratio = forecast / crop_median
    # Map ratio (weak demand <1 -> push markdown; strong demand >1 -> ease markdown)
    return float(np.clip(1.5 - 0.5 * ratio, 0.5, 1.8))


def price_recommendations(as_of_date: pd.Timestamp = None, live_window_days: int = 10) -> pd.DataFrame:
    """
    Prices only "currently live" inventory — listings posted within the last
    `live_window_days` relative to as_of_date. Pricing every historical listing
    against a single fixed "today" would make old listings look artificially
    stale (they were sold or delisted long ago in reality); a marketplace only
    ever needs live-inventory pricing.
    """
    listings = pd.read_csv(PROCESSED_DIR / "listings.csv", parse_dates=["listed_date", "harvest_date"])
    demand_summary = pd.read_csv(PROCESSED_DIR / "demand_forecast_summary.csv")

    if as_of_date is None:
        as_of_date = listings["listed_date"].max()

    df = listings[listings["listed_date"] >= as_of_date - pd.Timedelta(days=live_window_days)].copy()
    df["days_since_harvest"] = (as_of_date - df["harvest_date"]).dt.days.clip(lower=0)
    df["age_ratio"] = (df["days_since_harvest"] / df["shelf_life_days"]).clip(0, 1.5)
    df["base_markdown_pct"] = base_decay(df["age_ratio"].values)
    df["demand_adj"] = df["crop"].apply(lambda c: demand_adjustment(c, demand_summary))
    df["final_markdown_pct"] = np.clip(df["base_markdown_pct"] * df["demand_adj"], 0, 0.6)

    # A small premium allowance for very fresh + high-demand stock
    fresh_high_demand = (df["age_ratio"] < 0.15) & (df["demand_adj"] < 0.8)
    df.loc[fresh_high_demand, "final_markdown_pct"] = -0.05  # 5% premium

    df["recommended_price"] = (df["listing_price"] * (1 - df["final_markdown_pct"])).round(2)
    df["revenue_at_risk_if_unsold"] = (df["listing_price"] * df["quantity_kg"] * df["age_ratio"]).round(2)

    return df[["listing_id", "farmer_id", "crop", "listing_price", "quantity_kg",
               "days_since_harvest", "shelf_life_days", "age_ratio", "demand_adj",
               "final_markdown_pct", "recommended_price", "revenue_at_risk_if_unsold"]]


if __name__ == "__main__":
    recs = price_recommendations()
    recs.to_csv(PROCESSED_DIR / "pricing_recommendations.csv", index=False)

    print(f"Priced {len(recs)} listings.\n")
    print("Markdown distribution:")
    print(recs["final_markdown_pct"].describe().round(3))

    print("\nHighest revenue-at-risk listings (aging stock, act fast):")
    print(recs.sort_values("revenue_at_risk_if_unsold", ascending=False)
          [["listing_id", "crop", "age_ratio", "final_markdown_pct", "recommended_price",
            "revenue_at_risk_if_unsold"]].head(8).to_string(index=False))

    print(f"\nTotal revenue at risk across all current listings: "
          f"${recs['revenue_at_risk_if_unsold'].sum():,.2f}")
