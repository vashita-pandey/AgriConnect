"""
matching_recommender.py
=========================
Farmer-consumer matching: for a given consumer, ranks currently-live listings
by a transparent weighted score combining freshness, price-fit (relative to
that consumer's real price_sensitivity draw), distance, and an organic-match
bonus for sustainability-conscious consumers. Goes beyond the brief's basic
"browse and purchase" with an actual ranking model — the Azure Machine
Learning equivalent for this marketplace.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent))
from marketplace_entities import haversine_km

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

WEIGHTS = {"freshness": 0.30, "price_fit": 0.30, "distance": 0.30, "organic_bonus": 0.10}


def _normalize(s: pd.Series) -> pd.Series:
    rng = s.max() - s.min()
    return (s - s.min()) / rng if rng > 0 else s * 0 + 0.5


def score_listings_for_consumer(consumer: pd.Series, listings: pd.DataFrame, farmers: pd.DataFrame,
                                 as_of_date: pd.Timestamp, live_window_days: int = 10) -> pd.DataFrame:
    live = listings[listings["listed_date"] >= as_of_date - pd.Timedelta(days=live_window_days)].copy()
    live = live.merge(farmers[["farmer_id", "latitude", "longitude", "organic_certified"]],
                       on="farmer_id", how="left")

    live["days_since_harvest"] = (as_of_date - live["harvest_date"]).dt.days.clip(lower=0)
    live["freshness"] = 1 - (live["days_since_harvest"] / live["shelf_life_days"]).clip(0, 1)

    live["distance_km"] = haversine_km(consumer["latitude"], consumer["longitude"],
                                        live["latitude"], live["longitude"])
    live["distance_score"] = 1 - _normalize(live["distance_km"])

    # Price-fit: score is higher for cheaper-than-market listings, weighted by
    # this specific consumer's real price_sensitivity draw
    live["price_vs_market"] = live["listing_price"] / live["market_price_ref"]
    live["price_fit"] = 1 - _normalize(live["price_vs_market"]) * (0.4 + consumer["price_sensitivity"])
    live["price_fit"] = live["price_fit"].clip(0, 1)

    live["organic_bonus"] = np.where(
        consumer["sustainability_conscious"] and True, live["organic_certified"].astype(float), 0.0
    )

    live["match_score"] = (
        WEIGHTS["freshness"] * live["freshness"] +
        WEIGHTS["price_fit"] * live["price_fit"] +
        WEIGHTS["distance"] * live["distance_score"] +
        WEIGHTS["organic_bonus"] * live["organic_bonus"]
    ).round(4)

    return live.sort_values("match_score", ascending=False)


def top_matches_for_all_consumers(top_n: int = 5, sample_consumers: int = 100) -> pd.DataFrame:
    listings = pd.read_csv(PROCESSED_DIR / "listings.csv", parse_dates=["listed_date", "harvest_date"])
    farmers = pd.read_csv(PROCESSED_DIR / "farmers.csv")
    consumers = pd.read_csv(PROCESSED_DIR / "consumers.csv")
    as_of_date = listings["listed_date"].max()

    sample = consumers.sample(min(sample_consumers, len(consumers)), random_state=7)
    rows = []
    for _, cons in sample.iterrows():
        scored = score_listings_for_consumer(cons, listings, farmers, as_of_date)
        for _, r in scored.head(top_n).iterrows():
            rows.append({
                "consumer_id": cons["consumer_id"], "listing_id": r["listing_id"],
                "crop": r["crop"], "match_score": r["match_score"],
                "distance_km": round(r["distance_km"], 1), "freshness": round(r["freshness"], 2),
                "recommended_price": r["listing_price"],
            })
    result = pd.DataFrame(rows)
    result.to_csv(PROCESSED_DIR / "recommendations.csv", index=False)
    return result


if __name__ == "__main__":
    matches = top_matches_for_all_consumers(top_n=5, sample_consumers=100)
    print(f"Generated top-5 recommendations for {matches['consumer_id'].nunique()} consumers "
          f"({len(matches)} total recommendation rows)\n")
    print("Sample recommendations:")
    for cid in matches["consumer_id"].unique()[:3]:
        sub = matches[matches["consumer_id"] == cid]
        print(f"\n  {cid}:")
        for _, r in sub.iterrows():
            print(f"    -> {r['crop']} (score={r['match_score']}, {r['distance_km']}km, "
                  f"freshness={r['freshness']}, ${r['recommended_price']})")
