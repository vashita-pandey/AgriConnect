# AgriConnect — Cloud-Based Local Produce Marketplace
### VIT–Azure Internship (AZ-900) — Project P14

**Platform correction note:** this build was initially architected on AWS
based on a mistaken assumption about which cloud platform the internship
uses. The program's guidelines document confirmed the project must use
**Azure services from the approved list** (aligned with AZ-900 / Microsoft
Azure Fundamentals). Every service below is drawn directly from that
approved list — this is a full re-architecture, not a relabeling.

## 1. Objective mapping (brief → build)

| Brief requirement | How it's satisfied |
|---|---|
| Farmers list products, manage inventory | Listing + inventory data model with real price grounding |
| Consumers browse, purchase, learn sustainable ag | Marketplace browse/search + sustainability scoring per transaction |
| Notifications between farmers & consumers | Azure Event Grid → Functions → Communication Services/Notification Hubs pattern notification engine (order, price-drop, restock alerts) |
| Weather data informing best season for produce | Weather-driven harvest advisory engine on real historical temperature data |
| Rating & feedback system | Review sentiment + quality-risk engine (NLP) |
| Subscription model for regular deliveries | Subscription churn/retention model |

## 2. Beyond the brief — research-grade additions

| Engine | Why it matters for a real marketplace |
|---|---|
| Demand forecasting | Farmers need to know what to plant/list before, not after, demand shifts |
| Surplus-aware dynamic pricing | Produce is perishable — unsold stock loses value daily; static pricing loses money |
| Farmer–consumer matching | Distance + freshness + price-fit recommendation, not just keyword search |
| Sustainability / food-miles scoring | Directly extends the brief's "learn about sustainable agriculture" objective with a real number per order |
| Review sentiment & quality-risk | Early-warning on quality complaints before they tank a farmer's rating |
| Subscription churn model | Predicts which recurring-box subscribers are about to cancel |
| A/B testing framework | Reusable for pricing experiments, listing copy, notification timing |

## 3. Azure architecture

Built strictly from the program's approved services list: Azure Virtual
Machines (#1), Azure Blob Storage (#8), Azure SQL Database (#9), Azure
Functions (#11), Azure Event Grid (#22), Azure Notification Hubs (#19) /
Azure Communication Services (#20), Azure Machine Learning (#26), Power BI (#27).

```
        Farmers                                Consumers
    (list produce, set price,           (browse, search, purchase,
     manage inventory)                   subscribe, rate & review)
          │                                        │
          ▼                                        ▼
   ┌───────────────── Azure Virtual Machines (app servers) ─────────────────┐
   │              Marketplace application (listings, orders, auth)          │
   │                    B-series burstable, pay-as-you-go                   │
   └───────────────┬───────────────────────────────────┬────────────────────┘
                    ▼                                   ▼
        Azure SQL Database                     Azure Blob Storage
        (Basic/Serverless tier)                 (Hot tier)
        users · listings · orders               produce photos, docs
        subscriptions · reviews
                    │
                    ▼
         Azure Event Grid ── triggers ──▶ Azure Functions (Consumption)
   (price change, low stock,                        │
    forecast refresh, churn alert)                   ▼
                    │                  Azure Communication Services /
                    │                     Notification Hubs
                    │                (order confirmations, price-drop
                    │                  alerts, restock, renewals)
    ┌───────────────┼────────────────────────────────────┐
    ▼                ▼                                    ▼
Demand forecasting  Dynamic pricing engine      Matching / recommender
(Azure ML-pattern)   (perishability-aware)        (farmer ↔ consumer)
    │                │                                    │
    └────────┬───────┴───────────────┬────────────────────┘
             ▼                       ▼
   Sustainability scoring   Review sentiment / quality-risk
             │                       │
             └───────────┬───────────┘
                         ▼
       Streamlit Ops Dashboard (this build) + Power BI (execs)
```

**Reality check:** Azure SQL Database, Virtual Machines, and Communication
Services/Notification Hubs are provisioned, billed services — the app logic
and every ML engine are built and fully tested locally first (identical
interfaces to their Azure counterparts), with a real `azure-storage-blob`
integration for produce images/documents wired in directly, same
"one real managed-service integration + fully tested local equivalents for
the rest" pattern as the P55 build.

## 4. Data sources (real, not fabricated)

| Data | Source | Used for |
|---|---|---|
| `vegetable_prices.csv` — 287 days × 10 vegetables (2023) | GitHub-mirrored Kaggle dataset | Demand forecasting, dynamic pricing baseline |
| `reviews_raw.csv` — 23,486 real ratings + review text | GitHub-mirrored Kaggle "Women's Clothing E-Commerce Reviews" | Sentiment/quality-risk model training — **proxy dataset**: no public dataset ties real ratings+text to a produce marketplace, so we validate the NLP pipeline on real rating+text structure from this dataset (same honesty pattern as validating churn on Telco data in the P55 build), then apply it to marketplace reviews |
| `daily_weather_temp.csv` — 3,650 days real daily min. temperature (Melbourne) | GitHub-mirrored (Brownlee ML datasets) | Weather-driven harvest/seasonality advisory |
| Farmers, consumers, listings, orders, subscriptions | **Synthesized**, grounded in the real price data's category/seasonality structure | No public dataset ties real farms to real consumers — stated plainly, not hidden |

## 5. Repo structure

```
AgriConnect/
├── data/{raw,processed}/
├── engines/
│   ├── marketplace_entities.py   # farmers, consumers, listings, orders (grounded synthesis)
│   ├── demand_forecast.py        # per-crop time-series forecasting
│   ├── dynamic_pricing.py        # perishability-aware price optimization
│   ├── matching_recommender.py   # farmer-consumer matching
│   ├── sustainability_score.py   # food-miles / carbon scoring
│   ├── review_sentiment.py       # NLP quality-risk engine
│   ├── subscription_churn.py     # recurring delivery churn model
│   ├── weather_advisory.py       # harvest timing advisory
│   ├── notifications.py          # Event Grid/Functions/Communication Services-pattern engine
│   └── ab_testing.py             # reusable frequentist + Bayesian framework
├── cloud/
│   └── blob_adapter.py           # real azure-storage-blob integration
├── dashboard/
│   └── app.py                    # Streamlit multi-tab platform UI
├── architecture/
│   ├── PROJECT_PLAN.md
│   ├── architecture_diagram.py
│   └── build_deck.js
└── requirements.txt
```

## 6. Build phases

1. **Phase 1**: Marketplace entity generation (farmers/consumers/listings/orders) grounded in real price data + weather join
2. **Phase 2**: Demand forecasting + dynamic pricing (real time-series data)
3. **Phase 3**: Matching/recommender + sustainability scoring
4. **Phase 4**: Review sentiment/quality-risk + subscription churn + notifications
5. **Phase 5**: A/B testing + Streamlit dashboard
6. **Phase 6**: Architecture diagram + Azure Blob Storage integration + submission deck
7. **Phase 7**: Platform correction — AWS → Azure re-architecture (this revision)
