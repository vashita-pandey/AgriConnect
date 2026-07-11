"""
app.py — AgriConnect: Cloud-Based Local Produce Marketplace
Run with: streamlit run app.py (from the dashboard/ directory)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "engines"))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

st.set_page_config(page_title="AgriConnect — P14", layout="wide", page_icon="🌾")


@st.cache_data
def load_all():
    farmers = pd.read_csv(PROCESSED_DIR / "farmers.csv")
    consumers = pd.read_csv(PROCESSED_DIR / "consumers.csv")
    listings = pd.read_csv(PROCESSED_DIR / "listings.csv", parse_dates=["listed_date", "harvest_date"])
    orders = pd.read_csv(PROCESSED_DIR / "orders.csv", parse_dates=["order_date"])
    subs = pd.read_csv(PROCESSED_DIR / "subscription_churn_scores.csv")
    demand = pd.read_csv(PROCESSED_DIR / "demand_forecast_summary.csv")
    pricing = pd.read_csv(PROCESSED_DIR / "pricing_recommendations.csv")
    recs = pd.read_csv(PROCESSED_DIR / "recommendations.csv")
    sustainability = pd.read_csv(PROCESSED_DIR / "sustainability_scores.csv")
    reviews = pd.read_csv(PROCESSED_DIR / "marketplace_reviews.csv")
    farmer_quality = pd.read_csv(PROCESSED_DIR / "farmer_quality_risk.csv")
    weather_suit = pd.read_csv(PROCESSED_DIR / "weather_suitability.csv")
    notifications = pd.read_csv(PROCESSED_DIR / "notifications_log.csv")
    return (farmers, consumers, listings, orders, subs, demand, pricing, recs,
            sustainability, reviews, farmer_quality, weather_suit, notifications)


try:
    (farmers, consumers, listings, orders, subs, demand, pricing, recs,
     sustainability, reviews, farmer_quality, weather_suit, notifications) = load_all()
    DATA_READY = True
except FileNotFoundError as e:
    DATA_READY = False
    MISSING = str(e)

st.title("🌾 AgriConnect — Cloud-Based Local Produce Marketplace")
st.caption("P14 · VIT–Azure Internship (AZ-900) · Real vegetable price, review, and weather data grounding every engine")

if not DATA_READY:
    st.error(f"Processed data not found. Run the engines pipeline first.\n\n{MISSING}")
    st.code(
        "cd engines\n"
        "python3 marketplace_entities.py\npython3 demand_forecast.py\npython3 dynamic_pricing.py\n"
        "python3 matching_recommender.py\npython3 sustainability_score.py\npython3 review_sentiment.py\n"
        "python3 subscription_churn.py\npython3 notifications.py\npython3 weather_advisory.py\npython3 ab_testing.py"
    )
    st.stop()

tabs = st.tabs([
    "🏠 Overview", "🧑‍🌾 Farmers & Listings", "🛒 Orders & GMV", "📈 Demand Forecast",
    "💰 Dynamic Pricing", "🎯 Matching", "🌍 Sustainability", "⭐ Reviews & Quality",
    "📦 Subscriptions", "🌦️ Weather Advisory", "🧪 A/B Testing", "☁️ Architecture",
])

# ---------------------------------------------------------------------------
with tabs[0]:
    st.subheader("Platform KPIs")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Farmers", f"{len(farmers):,}")
    c2.metric("Consumers", f"{len(consumers):,}")
    c3.metric("Total Orders", f"{len(orders):,}")
    c4.metric("GMV", f"${orders['order_value'].sum():,.0f}")
    c5.metric("Active Subscriptions", int(subs["still_active"].sum()))

    col1, col2 = st.columns(2)
    with col1:
        crop_counts = orders["crop"].value_counts().reset_index()
        crop_counts.columns = ["crop", "orders"]
        fig = px.bar(crop_counts, x="crop", y="orders", title="Orders by Crop", color="crop")
        fig.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        region_counts = farmers["region"].value_counts().reset_index()
        region_counts.columns = ["region", "farmers"]
        fig = px.pie(region_counts, names="region", values="farmers", title="Farmers by Region", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    st.info(
        "**Data honesty note:** Vegetable prices, review text/ratings (proxy dataset), and weather "
        "are real. Farmers, consumers, listings, and orders are synthesized but grounded in real price "
        "data and a distance/price-sensitive choice model — see the Architecture tab for the full breakdown."
    )

# ---------------------------------------------------------------------------
with tabs[1]:
    st.subheader("Farmers & Live Listings")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Organic-certified farmers", f"{farmers['organic_certified'].mean():.1%}")
        st.dataframe(farmers[["farmer_id", "region", "years_farming", "organic_certified"]].head(20),
                     use_container_width=True, height=350)
    with col2:
        fig = px.scatter_mapbox(farmers, lat="latitude", lon="longitude", color="organic_certified",
                                 hover_data=["farmer_id", "region", "years_farming"],
                                 zoom=4, height=450, title="Farmer Locations")
        fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Live listings (last 10 days)**")
    live = listings[listings["listed_date"] >= listings["listed_date"].max() - pd.Timedelta(days=10)]
    st.dataframe(live[["listing_id", "farmer_id", "crop", "listing_price", "quantity_kg",
                        "listed_date"]].sort_values("listed_date", ascending=False).head(50),
                 use_container_width=True, height=300)

# ---------------------------------------------------------------------------
with tabs[2]:
    st.subheader("Orders & GMV")
    orders["month"] = orders["order_date"].dt.to_period("M").astype(str)
    monthly = orders.groupby("month").agg(gmv=("order_value", "sum"), n=("order_id", "count")).reset_index()
    fig = px.bar(monthly, x="month", y="gmv", title="GMV by Month")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(orders, x="distance_km", nbins=30, title="Order Delivery Distance Distribution")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        top_farmers = orders.groupby("farmer_id")["order_value"].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=top_farmers.index, y=top_farmers.values, title="Top 10 Farmers by Revenue")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
with tabs[3]:
    st.subheader("Demand Forecasting (14-day horizon)")
    st.caption("Price: OLS trend + day-of-week seasonality on the REAL 287-day price series. "
               "Elasticity: log-log regression on real transaction data.")
    st.dataframe(demand, use_container_width=True)

    crop_pick = st.selectbox("Select crop for price forecast detail", demand["crop"])
    import demand_forecast as df_engine
    price_series = df_engine.load_price_series()
    pf = df_engine.forecast_price(price_series, crop_pick)
    hist = price_series[["date", crop_pick]].rename(columns={crop_pick: "price"})
    fig = go.Figure()
    fig.add_scatter(x=hist["date"], y=hist["price"], name="Historical (real)", mode="lines")
    fig.add_scatter(x=pf["dates"], y=pf["forecast_price"], name="Forecast (14d)", mode="lines",
                     line=dict(dash="dash"))
    fig.update_layout(title=f"{crop_pick} — Real Price History + Forecast")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
with tabs[4]:
    st.subheader("Perishability-Aware Dynamic Pricing")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(pricing, x="final_markdown_pct", nbins=30, title="Markdown Distribution (live listings)")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.scatter(pricing, x="age_ratio", y="final_markdown_pct", color="crop",
                          title="Markdown vs. Inventory Age Ratio")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Highest revenue-at-risk listings (act fast)**")
    st.dataframe(
        pricing.sort_values("revenue_at_risk_if_unsold", ascending=False)
        [["listing_id", "farmer_id", "crop", "age_ratio", "final_markdown_pct",
          "recommended_price", "revenue_at_risk_if_unsold"]].head(20),
        use_container_width=True
    )
    st.metric("Total revenue at risk (live inventory)", f"${pricing['revenue_at_risk_if_unsold'].sum():,.0f}")

# ---------------------------------------------------------------------------
with tabs[5]:
    st.subheader("Farmer–Consumer Matching")
    cons_pick = st.selectbox("Select a consumer", recs["consumer_id"].unique())
    sub = recs[recs["consumer_id"] == cons_pick].sort_values("match_score", ascending=False)
    for _, r in sub.iterrows():
        st.progress(min(r["match_score"], 1.0),
                    text=f"{r['crop']} — score {r['match_score']} | {r['distance_km']}km | "
                         f"freshness {r['freshness']} | ${r['recommended_price']}")

    st.markdown("---")
    st.markdown("**Most-recommended crops across all sampled consumers**")
    crop_recs = recs["crop"].value_counts().reset_index()
    crop_recs.columns = ["crop", "times_recommended"]
    fig = px.bar(crop_recs, x="crop", y="times_recommended", title="Recommendation frequency by crop")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
with tabs[6]:
    st.subheader("Sustainability & Food-Miles Impact")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total emissions (local)", f"{sustainability['local_emissions_kg_co2'].sum():,.0f} kg CO2e")
    c2.metric("Baseline (conventional chain)", f"{sustainability['baseline_emissions_kg_co2'].sum():,.0f} kg CO2e")
    c3.metric("Avg. reduction per order", f"{sustainability['pct_reduction_vs_baseline'].mean():.1f}%")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(sustainability, x="sustainability_score", nbins=30, title="Sustainability Score Distribution")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        by_crop = sustainability.groupby("crop")["emissions_saved_kg_co2"].sum().sort_values(ascending=False)
        fig = px.bar(x=by_crop.index, y=by_crop.values, title="Emissions Saved by Crop (kg CO2e)")
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Methodology & assumptions"):
        st.write(
            "0.12 kg CO2e/tonne-km emission factor (mid-range published estimate for light freight), "
            "800 km conventional supply-chain baseline distance, plus 8 kg CO2e/tonne cold-storage "
            "overhead avoided by local same-day delivery. See engines/sustainability_score.py for full detail."
        )

# ---------------------------------------------------------------------------
with tabs[7]:
    st.subheader("Reviews & Quality-Risk (NLP)")
    st.caption("Sentiment classifier validated on real ratings+text data (91% accuracy, 0.96 ROC-AUC), "
               "applied here to marketplace reviews.")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(reviews, x="star_rating", nbins=5, title="Marketplace Review Star Rating Distribution")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.histogram(reviews, x="predicted_sentiment_proba", nbins=30, title="Predicted Sentiment Score Distribution")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Flagged quality-risk farmers: {int(farmer_quality['quality_risk_flag'].sum())} "
                f"of {(farmer_quality['n_reviews'] >= 3).sum()} eligible**")
    st.dataframe(
        farmer_quality[farmer_quality["quality_risk_flag"]].sort_values("avg_predicted_sentiment").head(20),
        use_container_width=True
    )

# ---------------------------------------------------------------------------
with tabs[8]:
    st.subheader("Subscription Retention")
    c1, c2 = st.columns(2)
    c1.metric("Active subscriptions", f"{int(subs['still_active'].sum())} / {len(subs)}")
    c2.metric("Retention rate", f"{subs['still_active'].mean():.1%}")

    col1, col2 = st.columns(2)
    with col1:
        tier_counts = subs["churn_risk_tier"].value_counts().reindex(["Low", "Medium", "High", "Critical"]).fillna(0)
        fig = px.bar(x=tier_counts.index, y=tier_counts.values,
                     color=tier_counts.index,
                     color_discrete_map={"Low": "#2ecc71", "Medium": "#f1c40f", "High": "#e67e22", "Critical": "#e74c3c"},
                     title="Churn Risk Tier Distribution")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.scatter(subs, x="box_value", y="churn_risk_score", color="frequency",
                          title="Churn Risk vs. Box Value")
        st.plotly_chart(fig, use_container_width=True)

    st.caption("Model: 5-fold cross-validated logistic regression (N=144 — cross-validation used "
               "because the sample is too small for a stable single-split estimate). ROC-AUC 0.577.")

# ---------------------------------------------------------------------------
with tabs[9]:
    st.subheader("Weather-Driven Harvest Advisory")
    st.caption("Real 10-year daily temperature series (Melbourne station data) x standard crop "
               "temperature-suitability ranges.")
    crop_pick2 = st.selectbox("Select crop", weather_suit["crop"].unique())
    sub = weather_suit[weather_suit["crop"] == crop_pick2].sort_values("month")
    fig = px.bar(sub, x="month", y="suitability_pct", title=f"{crop_pick2} — Monthly Growing Suitability (%)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Note: source data is Southern Hemisphere (Melbourne) — used to demonstrate the "
               "weather-integration methodology on a real, freely available long-run series. "
               "Production deployment would use a local station feed for the marketplace's actual region.")

# ---------------------------------------------------------------------------
with tabs[10]:
    st.subheader("A/B Testing Framework")
    import ab_testing as ab_engine
    result = ab_engine.analyze_organic_conversion()
    col1, col2 = st.columns(2)
    col1.metric("Non-organic conversion", f"{result['frequentist']['rate_a']:.1%}")
    col2.metric("Organic conversion", f"{result['frequentist']['rate_b']:.1%}",
                delta=f"{result['frequentist']['lift']:.1%}")
    st.write(f"p-value: {result['frequentist']['p_value']} "
             f"(significant at 95%: {result['frequentist']['significant_95']})")
    st.write(f"Bayesian P(organic beats non-organic): {result['bayesian']['prob_b_beats_a']}")
    st.info("Real finding: organic's ~12% price premium reduces conversion in this consumer base — "
            "price sensitivity outweighs quality preference here. Framework is fully reusable for any future test.")

    st.markdown("---")
    st.markdown("**Run your own A/B test**")
    c1, c2 = st.columns(2)
    with c1:
        conv_a = st.number_input("Variant A conversions", value=120, min_value=0)
        n_a = st.number_input("Variant A sample size", value=2000, min_value=1)
    with c2:
        conv_b = st.number_input("Variant B conversions", value=155, min_value=0)
        n_b = st.number_input("Variant B sample size", value=2000, min_value=1)
    if st.button("Run test"):
        demo = ab_engine.run_ab_test(int(conv_a), int(n_a), int(conv_b), int(n_b))
        c1, c2 = st.columns(2)
        c1.json(demo["frequentist"])
        c2.json(demo["bayesian"])

# ---------------------------------------------------------------------------
with tabs[11]:
    st.subheader("Target Azure Production Architecture")
    diagram_path = PROCESSED_DIR.parent.parent / "architecture" / "architecture_diagram.png"
    if diagram_path.exists():
        st.image(str(diagram_path), use_container_width=True)
    else:
        st.warning("Diagram not generated yet — run architecture/architecture_diagram.py")

    st.markdown("""
    | Component | This build | Production Azure |
    |---|---|---|
    | Marketplace app | Local Python/Streamlit | Azure Virtual Machines (B-series) |
    | Users, listings, orders, subscriptions | Local CSV | Azure SQL Database (Basic/Serverless tier) |
    | Produce images/documents | Local files | Azure Blob Storage (Hot tier) |
    | Event routing | `LocalNotificationHub` (identical trigger semantics) | Azure Event Grid |
    | Event/trigger processing | Local Python functions | Azure Functions (Consumption plan) |
    | Notifications | `LocalNotificationHub` | Azure Communication Services / Notification Hubs |
    | Demand forecasting, pricing, matching, sentiment | Local scikit-learn | Azure Machine Learning |
    | Dashboard | Streamlit | Streamlit (ops) + Power BI for execs |
    """)
