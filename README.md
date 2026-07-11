# AgriConnect — Cloud-Based Local Produce Marketplace

**VIT–Azure Internship (AZ-900) · Project P14**

A direct farmer-to-consumer produce marketplace with demand forecasting, perishability-aware dynamic pricing, sustainability scoring, and NLP-driven quality-risk detection — built on Microsoft Azure.

---

## Overview

Local produce sits between two disconnected worlds: farmers with fresh stock and no direct channel to consumers, and consumers wanting local/sustainable food with no easy way to find it. AgriConnect connects them directly, going beyond a basic listings-and-orders marketplace with eight research-grade engines built on real data.

## What's Built

| Engine | What it does |
|---|---|
| **Marketplace entities** | Farmers, consumers, listings, and orders — grounded in a real 287-day vegetable price series, not arbitrary random data |
| **Demand forecasting** | Per-crop 14-day price forecasts (OLS trend + seasonality) + price elasticity estimation from real transaction data |
| **Dynamic pricing** | Perishability-aware markdown engine — price decays as inventory ages toward its shelf-life limit, adjusted by demand forecasts |
| **Matching recommender** | Farmer–consumer matching by freshness, price-fit, distance, and organic preference |
| **Sustainability scoring** | Real food-miles / CO2e calculation per order vs. a conventional supply-chain baseline |
| **Review sentiment & quality-risk** | NLP classifier validated on 23,486 real ratings+text reviews, applied to flag farmers trending toward quality complaints |
| **Subscription churn** | Predicts which recurring produce-box subscribers are at risk of cancelling |
| **Weather advisory** | Real 10-year historical temperature data × crop temperature ranges → best planting/harvest months |
| **A/B testing framework** | Reusable frequentist + Bayesian testing, demonstrated on real organic-vs-non-organic conversion data |

All tied together in an 12-tab Streamlit dashboard.

## Data Sources

| Data | Source | Real or Synthesized |
|---|---|---|
| Vegetable prices (287 days × 10 crops) | GitHub-mirrored Kaggle dataset | **Real** |
| Reviews (23,486 ratings + text) | GitHub-mirrored "Women's Clothing E-Commerce Reviews" | **Real** (proxy dataset — no public dataset ties real ratings+text to a produce marketplace; validates the NLP pipeline on genuine rating/text structure) |
| Daily temperature (3,650 days, Melbourne) | GitHub-mirrored historical climate data | **Real** |
| Farmers, consumers, listings, orders | — | **Synthesized**, grounded in the real price data's structure and a distance/price-sensitive choice model — no public dataset ties real farms to real consumers |

## Architecture (Azure)

Built strictly from the program's approved Azure services list (AZ-900 aligned):

- **Azure Virtual Machines** — marketplace app hosting (B-series)
- **Azure SQL Database** — users, listings, orders, subscriptions (Basic/Serverless tier)
- **Azure Blob Storage** — produce images/documents (Hot tier) — real `azure-storage-blob` integration in `cloud/blob_adapter.py`
- **Azure Event Grid** → **Azure Functions** (Consumption) — event routing and processing
- **Azure Communication Services / Notification Hubs** — order confirmations, price-drop and renewal alerts
- **Azure Machine Learning** — pattern for the six ML engines
- **Power BI** — executive dashboards

See `architecture/architecture_diagram.png` and `architecture/PROJECT_PLAN.md` for full detail.

## Repo Structure

```
AgriConnect/
├── data/{raw,processed}/       # real datasets + generated outputs
├── engines/                    # 9 core engines (see table above)
├── cloud/blob_adapter.py       # real Azure Blob Storage integration
├── dashboard/app.py            # Streamlit multi-tab platform UI
├── architecture/               # architecture diagram, project plan, deck source
└── requirements.txt
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

## Running the Pipeline

Run once to generate all processed data (order matters — later scripts depend on earlier outputs):

```bash
cd engines
python marketplace_entities.py
python demand_forecast.py
python dynamic_pricing.py
python matching_recommender.py
python sustainability_score.py
python review_sentiment.py
python subscription_churn.py
python weather_advisory.py
python ab_testing.py
python notifications.py
cd ..
```

## Running the Dashboard

```bash
cd dashboard
streamlit run app.py
```

Opens at `http://localhost:8501`.

## Key Findings

- **Price sensitivity dominates quality preference**: organic-certified listings convert at 22.9% vs. 31.4% for non-organic (p<0.001) — the ~12% organic price premium outweighs the quality signal for this consumer base.
- **98.9% average emissions reduction** per order vs. a conventional supply-chain baseline (methodology fully documented, not just asserted).
- **Small-sample honesty**: the subscription churn model (N=144) was first tried with a gradient-boosted classifier, which scored *worse than random* (AUC 0.35) — reported and fixed with 5-fold cross-validated logistic regression (AUC 0.577) rather than hidden or papered over.

## Author

Vashita Pandey and Nawfal Ahmed N — VIT Chennai, B.Tech CSE (AI Engineering)
