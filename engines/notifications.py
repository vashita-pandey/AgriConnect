"""
notifications.py
==================
Local stand-in for the Azure notification pipeline the brief calls for:
Azure Event Grid (event routing) -> Azure Functions (Consumption plan,
processing) -> Azure Communication Services / Notification Hubs (actual
send). Same pattern as the rule-routing engines in the P55 build: identical
trigger/target interface to what the real Azure services would receive, so
swapping in real Azure SDK calls (azure-eventgrid, azure-communication-*) is
a config change, not a rewrite.

Triggers implemented:
  - order_confirmation       -> consumer, on every order
  - low_stock_alert          -> farmer, when listing quantity drops below threshold
  - price_drop_alert         -> consumers who favorited/ordered that crop before
  - subscription_renewal     -> consumer, ahead of a recurring box renewal
  - quality_risk_alert       -> farmer, when review_sentiment.py flags them
"""

import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from typing import Callable

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


@dataclass
class NotificationEvent:
    recipient_type: str   # "farmer" | "consumer"
    recipient_id: str
    channel: str           # "sms" | "email" | "push"
    template: str
    payload: dict


class LocalNotificationHub:
    """Mirrors Azure Event Grid topic-publish / Communication Services send semantics locally."""

    def __init__(self):
        self.sent: list[NotificationEvent] = []

    def publish(self, event: NotificationEvent):
        self.sent.append(event)

    def render(self, event: NotificationEvent) -> str:
        templates = {
            "order_confirmation": "Order confirmed: {quantity_kg}kg {crop} from {farmer_id} — ${order_value}",
            "low_stock_alert": "Low stock: only {quantity_kg}kg of {crop} left on listing {listing_id}",
            "price_drop_alert": "Price drop: {crop} now ${recommended_price} (was ${listing_price})",
            "subscription_renewal": "Your {frequency} produce box renews in 2 days — ${box_value}",
            "quality_risk_alert": "Your recent reviews are trending down (avg sentiment {avg_predicted_sentiment:.2f}). Consider reaching out to affected customers.",
        }
        return templates[event.template].format(**event.payload)


def generate_notifications() -> pd.DataFrame:
    hub = LocalNotificationHub()

    orders = pd.read_csv(PROCESSED_DIR / "orders.csv").tail(50)
    for _, o in orders.iterrows():
        hub.publish(NotificationEvent("consumer", o["consumer_id"], "email", "order_confirmation", o.to_dict()))

    listings = pd.read_csv(PROCESSED_DIR / "pricing_recommendations.csv")
    low_stock = listings.merge(
        pd.read_csv(PROCESSED_DIR / "listings.csv")[["listing_id", "quantity_kg"]].rename(
            columns={"quantity_kg": "qty_check"}),
        on="listing_id"
    )
    low_stock = low_stock[low_stock["qty_check"] < 20].head(20)
    for _, l in low_stock.iterrows():
        payload = {"quantity_kg": l["qty_check"], "crop": l["crop"], "listing_id": l["listing_id"]}
        hub.publish(NotificationEvent("farmer", l["farmer_id"], "sms", "low_stock_alert", payload))

    price_drops = listings[listings["final_markdown_pct"] > 0.15].head(20)
    for _, l in price_drops.iterrows():
        payload = {"crop": l["crop"], "recommended_price": l["recommended_price"],
                    "listing_price": l["listing_price"]}
        hub.publish(NotificationEvent("consumer", "SEGMENT:crop_followers", "push", "price_drop_alert", payload))

    subs = pd.read_csv(PROCESSED_DIR / "subscription_churn_scores.csv")
    active_subs = subs[subs["still_active"]].head(20)
    for _, s in active_subs.iterrows():
        payload = {"frequency": s["frequency"], "box_value": s["box_value"]}
        hub.publish(NotificationEvent("consumer", s["consumer_id"], "email", "subscription_renewal", payload))

    quality_risk = pd.read_csv(PROCESSED_DIR / "farmer_quality_risk.csv")
    flagged = quality_risk[quality_risk["quality_risk_flag"]].head(20)
    for _, f in flagged.iterrows():
        payload = {"avg_predicted_sentiment": f["avg_predicted_sentiment"]}
        hub.publish(NotificationEvent("farmer", f["farmer_id"], "email", "quality_risk_alert", payload))

    rows = [{
        "recipient_type": e.recipient_type, "recipient_id": e.recipient_id,
        "channel": e.channel, "template": e.template, "message": hub.render(e),
    } for e in hub.sent]
    result = pd.DataFrame(rows)
    result.to_csv(PROCESSED_DIR / "notifications_log.csv", index=False)
    return result


if __name__ == "__main__":
    result = generate_notifications()
    print(f"Generated {len(result)} notifications across {result['template'].nunique()} trigger types\n")
    print(result["template"].value_counts())
    print("\nSample messages:")
    for t in result["template"].unique():
        sample = result[result["template"] == t].iloc[0]
        print(f"  [{sample['channel']}] -> {sample['recipient_type']} {sample['recipient_id']}: {sample['message']}")
