"""
architecture_diagram.py — generates the target AZURE production architecture
diagram for AgriConnect (P14), built strictly from the program's approved
Azure services list, used in the dashboard and submission deck.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from pathlib import Path

NAVY = "#232F3E"
GREEN = "#3D8B37"     # produce/agriculture accent
AZURE_BLUE = "#0078D4"  # Microsoft Azure brand blue
LIGHT = "#F2F3F3"
WHITE = "#FFFFFF"
TEXT = "#16191F"

OUT_PATH = Path(__file__).resolve().parent / "architecture_diagram.png"


def box(ax, x, y, w, h, label, sublabel="", face=WHITE, edge=NAVY, textcolor=TEXT):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                        linewidth=1.8, edgecolor=edge, facecolor=face, zorder=2)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2 + (0.09 if sublabel else 0), label,
            ha="center", va="center", fontsize=9.5, fontweight="bold", color=textcolor, zorder=3)
    if sublabel:
        ax.text(x + w / 2, y + h / 2 - 0.14, sublabel,
                ha="center", va="center", fontsize=7.3, color=textcolor, zorder=3, style="italic")


def arrow(ax, xy_from, xy_to, color=NAVY):
    a = FancyArrowPatch(xy_from, xy_to, arrowstyle="-|>", mutation_scale=14,
                         linewidth=1.6, color=color, zorder=1)
    ax.add_patch(a)


fig, ax = plt.subplots(figsize=(13, 8.5))
ax.set_xlim(0, 13)
ax.set_ylim(0, 8.5)
ax.axis("off")
fig.patch.set_facecolor(WHITE)

ax.text(6.5, 8.1, "AgriConnect — Target Azure Production Architecture", ha="center",
        fontsize=15, fontweight="bold", color=NAVY)
ax.text(6.5, 7.75, "Cloud-Based Local Produce Marketplace · P14 · Built on approved AZ-900 services",
        ha="center", fontsize=9.5, color="#555555")

# Farmers / Consumers
box(ax, 0.4, 6.8, 3.0, 0.6, "Farmers", "list produce, manage inventory", face=GREEN, edge=NAVY, textcolor=WHITE)
box(ax, 9.6, 6.8, 3.0, 0.6, "Consumers", "browse, purchase, subscribe", face=GREEN, edge=NAVY, textcolor=WHITE)
arrow(ax, (1.9, 6.8), (5.5, 6.2))
arrow(ax, (11.1, 6.8), (7.5, 6.2))

# Azure VMs app server
box(ax, 3.9, 5.6, 5.2, 0.65, "Azure Virtual Machines", "marketplace application (B-series, burstable)",
    face=AZURE_BLUE, edge=NAVY, textcolor=WHITE)
arrow(ax, (5.3, 5.6), (2.5, 4.75))
arrow(ax, (7.8, 5.6), (10.2, 4.75))

# SQL Database + Blob Storage
box(ax, 0.9, 4.15, 3.2, 0.6, "Azure SQL Database", "users · listings · orders · subs (Basic/Serverless)", face=LIGHT, edge=NAVY)
box(ax, 9.0, 4.15, 3.2, 0.6, "Azure Blob Storage", "produce photos & documents (Hot tier)", face=LIGHT, edge=NAVY)
arrow(ax, (2.5, 4.15), (5.0, 3.55))
arrow(ax, (10.2, 4.15), (7.8, 3.55))

# Event Grid -> Functions -> Communication Services / Notification Hubs
box(ax, 4.6, 2.95, 3.8, 0.6, "Azure Event Grid", "routes triggers: price change, low stock, forecast refresh",
    face=AZURE_BLUE, edge=NAVY, textcolor=WHITE)
arrow(ax, (6.5, 2.95), (6.5, 2.35))
box(ax, 4.6, 1.75, 3.8, 0.6, "Azure Functions", "Consumption plan — processes each event", face=WHITE, edge=NAVY)
arrow(ax, (6.5, 1.75), (6.5, 1.15))
box(ax, 4.15, 0.55, 4.7, 0.6, "Azure Communication Services / Notification Hubs",
    "order confirmations, price-drop & renewal alerts", face=AZURE_BLUE, edge=NAVY, textcolor=WHITE)

# ML engines row (right side, feeding off SQL Database + Blob Storage)
engines = ["Demand\nForecasting", "Dynamic\nPricing", "Matching\nRecommender",
           "Sustainability\nScoring", "Review\nSentiment", "Churn &\nWeather"]
ax.text(10.8, 3.0, "Azure Machine\nLearning", ha="center", fontsize=10, fontweight="bold", color=NAVY)
for i, label in enumerate(engines):
    ex = 9.3 + (i % 3) * 1.15
    ey = 2.35 - (i // 3) * 0.85
    box(ax, ex, ey, 1.05, 0.7, label, face=LIGHT, edge=NAVY, textcolor=TEXT)
box(ax, 9.0, 0.15, 3.9, 0.35, "Power BI — executive dashboards", face=LIGHT, edge=NAVY)

# Streamlit dashboard callout
box(ax, 0.4, 3.3, 2.0, 0.5, "Streamlit Ops\nDashboard (this build)", face=NAVY, edge=NAVY, textcolor=WHITE)
arrow(ax, (2.4, 3.55), (4.6, 3.15))

# Legend
box(ax, 0.4, 0.15, 1.9, 0.5, "Live in this build", face=NAVY, edge=NAVY, textcolor=WHITE)
box(ax, 2.5, 0.15, 2.1, 0.5, "Azure managed service\n(architected)", face=AZURE_BLUE, edge=NAVY, textcolor=WHITE)

plt.tight_layout()
plt.savefig(OUT_PATH, dpi=170, facecolor=WHITE, bbox_inches="tight")
print(f"Saved architecture diagram -> {OUT_PATH}")
