"""
marketplace_entities.py
========================
Generates the AgriConnect marketplace universe: farmers, consumers, listings,
orders, and subscriptions — grounded in the REAL vegetable price time series
(vegetable_prices.csv, 287 days x 10 vegetables, 2023) rather than arbitrary
random numbers.

Why synthesize entities at all: no public dataset ties real farms to real
consumers with real transaction history (this doesn't exist for privacy/
competitive reasons even in production marketplaces' public data). What's real
is the underlying price/seasonality structure; every listing price is anchored
to the actual historical price series for that vegetable and date, and every
order is generated with a distance-and-price-sensitive choice model rather than
pure randomness.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import timedelta

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Real Indian cities used as anchors for synthetic geolocation (vegetable names
# in the price dataset are Indian produce terms — Bhindi, Brinjal, Methi, etc.)
CITY_ANCHORS = {
    "Bengaluru": (12.9716, 77.5946), "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867), "Pune": (18.5204, 73.8567),
    "Coimbatore": (11.0168, 76.9558), "Nashik": (19.9975, 73.7898),
}

VEGETABLES = ["Bhindi (Ladies finger)", "Tomato", "Onion", "Potato", "Brinjal",
              "Garlic", "Peas", "Methi", "Green Chilli", "Elephant Yam (Suran)"]

# Real, published perishability windows (days) — average produce shelf life
SHELF_LIFE_DAYS = {
    "Bhindi (Ladies finger)": 4, "Tomato": 7, "Onion": 30, "Potato": 60,
    "Brinjal": 5, "Garlic": 90, "Peas": 4, "Methi": 3, "Green Chilli": 10,
    "Elephant Yam (Suran)": 45,
}


def load_price_series() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "vegetable_prices.csv")
    df["Price Dates"] = pd.to_datetime(df["Price Dates"], format="%d-%m-%Y")
    return df.rename(columns={"Price Dates": "date"})


def _random_point_near(rng, lat, lon, radius_km=25):
    """Random point within radius_km of an anchor city (farmers ring rural areas around cities)."""
    r = radius_km * np.sqrt(rng.uniform(0, 1)) / 111.0  # convert km to degrees (approx)
    theta = rng.uniform(0, 2 * np.pi)
    return lat + r * np.cos(theta), lon + r * np.sin(theta)


def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def generate_farmers(n=150, seed=42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cities = list(CITY_ANCHORS.keys())
    rows = []
    for i in range(n):
        city = rng.choice(cities)
        lat0, lon0 = CITY_ANCHORS[city]
        lat, lon = _random_point_near(rng, lat0, lon0, radius_km=rng.uniform(10, 40))
        n_crops = rng.integers(1, 4)
        specialties = list(rng.choice(VEGETABLES, size=n_crops, replace=False))
        rows.append({
            "farmer_id": f"FARM-{i:04d}",
            "region": city,
            "latitude": round(lat, 5), "longitude": round(lon, 5),
            "specialties": specialties,
            "years_farming": int(rng.integers(1, 35)),
            "organic_certified": bool(rng.random() < 0.28),
        })
    return pd.DataFrame(rows)


def generate_consumers(n=800, seed=43) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cities = list(CITY_ANCHORS.keys())
    rows = []
    for i in range(n):
        city = rng.choice(cities)
        lat0, lon0 = CITY_ANCHORS[city]
        lat, lon = _random_point_near(rng, lat0, lon0, radius_km=rng.uniform(1, 15))
        rows.append({
            "consumer_id": f"CONS-{i:04d}",
            "city": city,
            "latitude": round(lat, 5), "longitude": round(lon, 5),
            "price_sensitivity": float(rng.beta(2, 2)),  # 0=price-insensitive, 1=very sensitive
            "sustainability_conscious": bool(rng.random() < 0.35),
        })
    return pd.DataFrame(rows)


def generate_listings(farmers: pd.DataFrame, price_series: pd.DataFrame, seed=44) -> pd.DataFrame:
    """
    Each farmer lists their specialty vegetables on a rolling basis. Listing
    price = that day's REAL market price +/- a small farmer-specific markup/
    discount (organic certified farmers price ~12% higher, matching real-world
    organic premiums), with inventory quantity and a harvest date driving
    freshness/perishability.
    """
    rng = np.random.default_rng(seed)
    rows = []
    dates = price_series["date"].tolist()
    listing_id = 0
    for _, farmer in farmers.iterrows():
        # Each farmer lists ~2x per week per specialty crop over the dataset's date range
        for crop in farmer["specialties"]:
            crop_dates = rng.choice(dates, size=min(40, len(dates)), replace=False)
            for d in crop_dates:
                market_price = price_series.loc[price_series["date"] == d, crop].values[0]
                markup = 1.12 if farmer["organic_certified"] else 1.0
                farmer_variation = rng.normal(1.0, 0.08)
                listing_price = round(max(market_price * markup * farmer_variation, 1), 2)
                harvest_date = pd.Timestamp(d) - timedelta(days=int(rng.integers(0, 2)))
                rows.append({
                    "listing_id": f"LST-{listing_id:06d}",
                    "farmer_id": farmer["farmer_id"],
                    "crop": crop,
                    "listed_date": d,
                    "harvest_date": harvest_date,
                    "market_price_ref": market_price,
                    "listing_price": listing_price,
                    "quantity_kg": int(rng.integers(10, 200)),
                    "shelf_life_days": SHELF_LIFE_DAYS[crop],
                })
                listing_id += 1
    return pd.DataFrame(rows)


def generate_orders(consumers: pd.DataFrame, listings: pd.DataFrame, farmers: pd.DataFrame,
                     n_orders=6000, seed=45) -> pd.DataFrame:
    """
    Consumers choose listings with a distance + price-sensitivity weighted
    choice model: closer + cheaper listings are more likely to be bought,
    modulated by each consumer's real price_sensitivity draw.
    """
    rng = np.random.default_rng(seed)
    farmer_loc = farmers.set_index("farmer_id")[["latitude", "longitude"]]
    listings = listings.merge(farmer_loc, on="farmer_id", how="left")

    rows = []
    consumer_ids = consumers["consumer_id"].values
    for i in range(n_orders):
        cons = consumers.iloc[rng.integers(0, len(consumers))]
        # Candidate listings: sample a pool, then weight by distance/price
        pool = listings.sample(min(60, len(listings)), random_state=int(rng.integers(0, 1e6)))
        dist = haversine_km(cons["latitude"], cons["longitude"], pool["latitude"], pool["longitude"])
        price_penalty = pool["listing_price"] * (0.5 + cons["price_sensitivity"])
        dist_penalty = dist * (1.0 + cons["price_sensitivity"] * 0.5)
        score = 1 / (1 + price_penalty * 0.05 + dist_penalty * 0.1)
        chosen = pool.iloc[np.argmax(score.values * rng.uniform(0.7, 1.3, size=len(score)))]

        qty = int(rng.integers(1, min(10, max(2, chosen["quantity_kg"] // 5))))
        order_date = pd.Timestamp(chosen["listed_date"]) + timedelta(days=int(rng.integers(0, 3)))
        rows.append({
            "order_id": f"ORD-{i:06d}",
            "consumer_id": cons["consumer_id"],
            "listing_id": chosen["listing_id"],
            "farmer_id": chosen["farmer_id"],
            "crop": chosen["crop"],
            "order_date": order_date,
            "quantity_kg": qty,
            "unit_price": chosen["listing_price"],
            "order_value": round(qty * chosen["listing_price"], 2),
            "distance_km": round(haversine_km(cons["latitude"], cons["longitude"],
                                               chosen["latitude"], chosen["longitude"]), 1),
        })
    return pd.DataFrame(rows)


def generate_subscriptions(consumers: pd.DataFrame, seed=46) -> pd.DataFrame:
    """
    ~18% of consumers subscribe to a recurring produce box (brief's subscription
    objective). Retention is DELIBERATELY made feature-dependent (not pure noise)
    so a churn classifier trained on this data recovers genuine, explainable signal
    rather than fitting noise: higher price sensitivity, higher box value relative
    to that sensitivity, and shorter tenure all real-world raise churn risk.
    """
    rng = np.random.default_rng(seed)
    subs = consumers.sample(frac=0.18, random_state=seed).copy()
    subs["subscription_id"] = ["SUB-{:04d}".format(i) for i in range(len(subs))]
    subs["frequency"] = rng.choice(["Weekly", "Biweekly", "Monthly"], size=len(subs), p=[0.5, 0.35, 0.15])
    tenure_days = rng.integers(5, 200, size=len(subs))
    subs["start_date"] = pd.Timestamp("2023-07-01") - pd.to_timedelta(tenure_days, unit="D")
    subs["box_value"] = rng.uniform(150, 600, size=len(subs)).round(2)
    subs["tenure_days"] = tenure_days

    freq_risk = subs["frequency"].map({"Weekly": 0.05, "Biweekly": 0.0, "Monthly": -0.05}).values
    value_risk = (subs["box_value"] - 150) / (600 - 150) * subs["price_sensitivity"].values * 0.35
    tenure_protection = np.clip(tenure_days / 200, 0, 1) * 0.30  # longer tenure = "sunk cost" retention
    churn_logit = -0.9 + subs["price_sensitivity"].values * 0.6 + value_risk + freq_risk - tenure_protection
    churn_prob = 1 / (1 + np.exp(-churn_logit))
    subs["still_active"] = rng.random(len(subs)) > churn_prob

    return subs[["subscription_id", "consumer_id", "frequency", "start_date", "tenure_days",
                  "box_value", "price_sensitivity", "still_active"]]


if __name__ == "__main__":
    price_series = load_price_series()
    print(f"Loaded real price series: {len(price_series)} days x {len(VEGETABLES)} vegetables")

    farmers = generate_farmers()
    consumers = generate_consumers()
    listings = generate_listings(farmers, price_series)
    orders = generate_orders(consumers, listings, farmers)
    subs = generate_subscriptions(consumers)

    farmers.to_csv(PROCESSED_DIR / "farmers.csv", index=False)
    consumers.to_csv(PROCESSED_DIR / "consumers.csv", index=False)
    listings.to_csv(PROCESSED_DIR / "listings.csv", index=False)
    orders.to_csv(PROCESSED_DIR / "orders.csv", index=False)
    subs.to_csv(PROCESSED_DIR / "subscriptions.csv", index=False)

    print(f"Farmers: {len(farmers)}  Consumers: {len(consumers)}")
    print(f"Listings: {len(listings)}  Orders: {len(orders)}  Subscriptions: {len(subs)}")
    print(f"\nTotal GMV (orders): ${orders['order_value'].sum():,.2f}")
    print(f"Avg order distance: {orders['distance_km'].mean():.1f} km")
    print(f"\nOrders by crop:\n{orders['crop'].value_counts()}")
