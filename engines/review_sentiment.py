"""
review_sentiment.py
=====================
Two-stage, honestly-scoped NLP pipeline:

1. VALIDATE on real data — trains a TF-IDF + Logistic Regression sentiment
   classifier on the REAL reviews_raw.csv (23,486 real ratings + review text).
   This is a genuine proxy dataset (women's clothing e-commerce, not produce),
   used exactly like the Telco-churn validation in the P55 build: no public
   dataset ties real ratings+text to a produce marketplace, so we prove the
   NLP pipeline works on real rating/text structure first, with honestly
   reported metrics.

2. APPLY to marketplace reviews — generates synthetic marketplace reviews from
   a small realistic template bank, weighted by each farmer's real underlying
   quality signal (organic certification + years farming), then runs the
   REAL-DATA-VALIDATED sentiment model on this text to score them, and flags
   any farmer trending toward negative sentiment as a quality-risk case.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

POSITIVE_TEMPLATES = [
    "The {crop} was incredibly fresh and flavorful, will definitely order again.",
    "Great quality {crop}, arrived quickly and tasted like it was picked yesterday.",
    "Really impressed with this farmer's {crop} - consistent quality every time.",
    "Best {crop} I've bought locally, well worth the price.",
    "Excellent produce, the {crop} lasted much longer than store-bought.",
]
NEGATIVE_TEMPLATES = [
    "The {crop} arrived bruised and past its best, disappointed with this order.",
    "Quality was inconsistent, some of the {crop} was already going bad.",
    "Not fresh at all, the {crop} looked days old when it arrived.",
    "Overpriced for the quality of {crop} received, wouldn't order again.",
    "Packaging was poor and the {crop} was damaged in transit.",
]
NEUTRAL_TEMPLATES = [
    "The {crop} was okay, nothing special but acceptable.",
    "Average {crop}, arrived on time.",
    "Decent quality {crop} for the price.",
]


def train_sentiment_model() -> dict:
    df = pd.read_csv(RAW_DIR / "reviews_raw.csv")
    df = df.dropna(subset=["Review Text", "Rating"])
    df = df[df["Rating"] != 3]  # standard practice: drop neutral, as in published analyses of this dataset
    df["label"] = (df["Rating"] >= 4).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        df["Review Text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english", ngram_range=(1, 2))
    Xtr = vectorizer.fit_transform(X_train)
    Xte = vectorizer.transform(X_test)

    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(Xtr, y_train)

    preds = model.predict(Xte)
    proba = model.predict_proba(Xte)[:, 1]

    metrics = {
        "n_train": len(X_train), "n_test": len(X_test),
        "accuracy": round(accuracy_score(y_test, preds), 4),
        "roc_auc": round(roc_auc_score(y_test, proba), 4),
    }
    return {"model": model, "vectorizer": vectorizer, "metrics": metrics}


def generate_marketplace_reviews(n_reviews: int = 2000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    farmers = pd.read_csv(PROCESSED_DIR / "farmers.csv")
    orders = pd.read_csv(PROCESSED_DIR / "orders.csv")

    farmers["quality_signal"] = (
        0.5 * farmers["organic_certified"].astype(float) +
        0.5 * np.clip(farmers["years_farming"] / 35, 0, 1)
    )

    sample_orders = orders.sample(min(n_reviews, len(orders)), random_state=seed)
    rows = []
    for _, order in sample_orders.iterrows():
        farmer = farmers[farmers["farmer_id"] == order["farmer_id"]]
        if farmer.empty:
            continue
        q = farmer.iloc[0]["quality_signal"]
        # Higher quality signal -> more likely positive review, with noise.
        # Calibrated so an average-quality farmer (q~0.35) still lands mostly
        # positive/neutral, matching real marketplace rating distributions
        # (most sellers cluster around good-not-perfect; a minority are genuine
        # quality-risk outliers) rather than a broad negative skew.
        p_negative_base = 0.08
        p_positive = 0.40 + 0.55 * q
        p_neutral = 0.12
        roll = rng.random()
        if roll < p_negative_base:
            template_pool, rating = NEGATIVE_TEMPLATES, rng.integers(1, 3)
        elif roll < p_negative_base + p_positive:
            template_pool, rating = POSITIVE_TEMPLATES, rng.integers(4, 6)
        elif roll < p_negative_base + p_positive + p_neutral:
            template_pool, rating = NEUTRAL_TEMPLATES, 3
        else:
            template_pool, rating = NEGATIVE_TEMPLATES, rng.integers(1, 3)

        text = rng.choice(template_pool).format(crop=order["crop"].split(" (")[0])
        rows.append({
            "order_id": order["order_id"], "farmer_id": order["farmer_id"],
            "crop": order["crop"], "review_text": text, "star_rating": rating,
        })
    return pd.DataFrame(rows)


def run_quality_risk_analysis() -> dict:
    trained = train_sentiment_model()
    reviews = generate_marketplace_reviews()

    X = trained["vectorizer"].transform(reviews["review_text"])
    reviews["predicted_sentiment_proba"] = trained["model"].predict_proba(X)[:, 1]

    farmer_quality = reviews.groupby("farmer_id").agg(
        n_reviews=("order_id", "count"),
        avg_star_rating=("star_rating", "mean"),
        avg_predicted_sentiment=("predicted_sentiment_proba", "mean"),
    ).reset_index()
    farmer_quality["quality_risk_flag"] = (
        (farmer_quality["avg_predicted_sentiment"] < 0.4) & (farmer_quality["n_reviews"] >= 3)
    )

    reviews.to_csv(PROCESSED_DIR / "marketplace_reviews.csv", index=False)
    farmer_quality.to_csv(PROCESSED_DIR / "farmer_quality_risk.csv", index=False)

    return {"metrics": trained["metrics"], "reviews": reviews, "farmer_quality": farmer_quality}


if __name__ == "__main__":
    results = run_quality_risk_analysis()
    print("=" * 60)
    print("Sentiment classifier — validated on REAL review data")
    print("=" * 60)
    print(f"Train/test: {results['metrics']['n_train']}/{results['metrics']['n_test']}")
    print(f"Accuracy: {results['metrics']['accuracy']}   ROC-AUC: {results['metrics']['roc_auc']}\n")

    print("=" * 60)
    print("Applied to marketplace reviews (synthetic text, real farmer quality signal)")
    print("=" * 60)
    fq = results["farmer_quality"]
    print(f"Farmers with >=3 marketplace reviews: {(fq['n_reviews'] >= 3).sum()}")
    print(f"Flagged quality-risk farmers: {fq['quality_risk_flag'].sum()}\n")
    print("Sample flagged farmers:")
    print(fq[fq["quality_risk_flag"]].head(5).to_string(index=False))
