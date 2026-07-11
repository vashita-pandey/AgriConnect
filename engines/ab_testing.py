"""
ab_testing.py
==============
Reusable frequentist + Bayesian A/B testing framework (same core as the P55
build), applied here to a genuine marketplace question answerable from our
grounded data: does organic certification improve a listing's conversion rate
(fraction of listings that receive at least one order)?
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def two_proportion_ztest(conv_a: int, n_a: int, conv_b: int, n_b: int) -> dict:
    p_a, p_b = conv_a / n_a, conv_b / n_b
    p_pool = (conv_a + conv_b) / (n_a + n_b)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    z = (p_b - p_a) / se if se > 0 else 0.0
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    return {
        "rate_a": round(p_a, 4), "rate_b": round(p_b, 4),
        "lift": round((p_b - p_a) / p_a, 4) if p_a > 0 else None,
        "z_stat": round(float(z), 4), "p_value": round(float(p_value), 5),
        "significant_95": bool(p_value < 0.05),
    }


def bayesian_beta_binomial(conv_a: int, n_a: int, conv_b: int, n_b: int,
                            n_samples: int = 200000, seed: int = 42) -> dict:
    rng = np.random.default_rng(seed)
    post_a = rng.beta(1 + conv_a, 1 + n_a - conv_a, n_samples)
    post_b = rng.beta(1 + conv_b, 1 + n_b - conv_b, n_samples)
    return {
        "posterior_mean_a": round(float(post_a.mean()), 4),
        "posterior_mean_b": round(float(post_b.mean()), 4),
        "prob_b_beats_a": round(float(np.mean(post_b > post_a)), 4),
    }


def run_ab_test(conv_a: int, n_a: int, conv_b: int, n_b: int, label_a="A", label_b="B") -> dict:
    return {"variant_a": label_a, "variant_b": label_b,
            "frequentist": two_proportion_ztest(conv_a, n_a, conv_b, n_b),
            "bayesian": bayesian_beta_binomial(conv_a, n_a, conv_b, n_b)}


def analyze_organic_conversion() -> dict:
    listings = pd.read_csv(PROCESSED_DIR / "listings.csv")
    orders = pd.read_csv(PROCESSED_DIR / "orders.csv")
    farmers = pd.read_csv(PROCESSED_DIR / "farmers.csv")

    listings = listings.merge(farmers[["farmer_id", "organic_certified"]], on="farmer_id")
    ordered_listing_ids = set(orders["listing_id"])
    listings["converted"] = listings["listing_id"].isin(ordered_listing_ids)

    organic = listings[listings["organic_certified"]]
    non_organic = listings[~listings["organic_certified"]]

    conv_organic, n_organic = int(organic["converted"].sum()), len(organic)
    conv_non, n_non = int(non_organic["converted"].sum()), len(non_organic)

    result = run_ab_test(conv_non, n_non, conv_organic, n_organic,
                          label_a="Non-organic", label_b="Organic")
    return result


if __name__ == "__main__":
    result = analyze_organic_conversion()
    print("A/B test: Organic-certified vs. non-organic listing conversion rate\n")
    print(f"Non-organic: {result['frequentist']['rate_a']:.2%}")
    print(f"Organic:     {result['frequentist']['rate_b']:.2%}")
    print(f"Lift: {result['frequentist']['lift']}")
    print(f"p-value: {result['frequentist']['p_value']}  (significant at 95%: {result['frequentist']['significant_95']})")
    print(f"Bayesian P(organic beats non-organic): {result['bayesian']['prob_b_beats_a']}")

    print("\n--- Framework demo on a hypothetical test (reusable API) ---")
    demo = run_ab_test(conv_a=120, n_a=2000, conv_b=155, n_b=2000,
                        label_a="Listing photo A", label_b="Listing photo B")
    print(demo)
