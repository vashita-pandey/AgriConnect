const pptxgen = require("pptxgenjs");

const NAVY = "232F3E";
const GREEN = "3D8B37";
const ORANGE = "FF9900";
const LIGHT = "F2F3F3";
const SLATE = "5A6472";
const WHITE = "FFFFFF";
const DARKTEXT = "16191F";

let pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Vashita Pandey";
pres.title = "AgriConnect — P14";

const W = 13.3, H = 7.5;

function titleBar(slide, kicker, title) {
  slide.addText(kicker.toUpperCase(), { x: 0.6, y: 0.35, w: 10, h: 0.35, fontSize: 12, color: GREEN, bold: true, charSpacing: 2, fontFace: "Calibri" });
  slide.addText(title, { x: 0.6, y: 0.65, w: 12.1, h: 0.9, fontSize: 30, color: NAVY, bold: true, fontFace: "Cambria" });
}
function pageNum(slide, n) {
  slide.addText(String(n), { x: W - 0.7, y: H - 0.5, w: 0.4, h: 0.3, fontSize: 10, color: SLATE, align: "right" });
}
function card(slide, x, y, w, h, fill = WHITE) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.08, fill: { color: fill },
    line: { color: "E2E4E7", width: 1 },
    shadow: { type: "outer", color: "000000", blur: 8, offset: 3, angle: 90, opacity: 0.10 },
  });
}

// Slide 1 — Title
{
  let s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("P14", { x: 0.8, y: 1.5, w: 4, h: 0.6, fontSize: 16, color: GREEN, bold: true, charSpacing: 3, fontFace: "Calibri" });
  s.addText("AgriConnect", { x: 0.8, y: 2.0, w: 11.5, h: 1.2, fontSize: 48, color: WHITE, bold: true, fontFace: "Cambria" });
  s.addText("Cloud-Based Local Produce Marketplace", { x: 0.8, y: 3.1, w: 11.5, h: 0.8, fontSize: 24, color: "CBD3DC", fontFace: "Cambria" });
  s.addText("Connecting farmers and consumers directly — with demand forecasting, perishability-aware pricing, sustainability scoring, and quality-risk detection built on real data.",
    { x: 0.8, y: 4.15, w: 9.5, h: 0.9, fontSize: 14, color: "CBD3DC", fontFace: "Calibri" });
  s.addText("VIT–Azure Internship (AZ-900)  ·  Vashita Pandey  ·  2026", { x: 0.8, y: 6.6, w: 8, h: 0.4, fontSize: 12, color: GREEN, bold: true, fontFace: "Calibri" });
}

// Slide 2 — Problem
{
  let s = pres.addSlide();
  titleBar(s, "Project Overview", "The Problem: Farmers and Consumers Are Disconnected");
  card(s, 0.6, 1.9, 6.1, 4.7);
  s.addText([
    { text: "Local produce sits between two disconnected worlds", options: { bold: true, breakLine: true, color: NAVY, fontSize: 16 } },
    { text: "farmers with fresh stock and no direct channel, consumers wanting local/sustainable food with no easy way to find it.", options: { breakLine: true, color: DARKTEXT, fontSize: 13 } },
    { text: " ", options: { breakLine: true, fontSize: 8 } },
    { text: "Farmers can't reach beyond local footfall", options: { bullet: true, breakLine: true, bold: true, color: NAVY, fontSize: 13 } },
    { text: "Produce is perishable — static pricing loses money daily", options: { bullet: true, breakLine: true, bold: true, color: NAVY, fontSize: 13 } },
    { text: "No visibility into true environmental/sustainability impact", options: { bullet: true, breakLine: true, bold: true, color: NAVY, fontSize: 13 } },
    { text: "No early warning when a farmer's quality is slipping", options: { bullet: true, bold: true, color: NAVY, fontSize: 13 } },
  ], { x: 1.0, y: 2.2, w: 5.4, h: 4.2, valign: "top" });

  card(s, 7.0, 1.9, 5.7, 4.7, NAVY);
  s.addText("What we're building", { x: 7.4, y: 2.15, w: 5, h: 0.4, fontSize: 15, bold: true, color: GREEN, fontFace: "Calibri" });
  s.addText([
    { text: "Direct farmer-to-consumer marketplace with real inventory & pricing", options: { bullet: true, breakLine: true, color: WHITE, fontSize: 12.5 } },
    { text: "Demand forecasting so farmers plant/list ahead of demand", options: { bullet: true, breakLine: true, color: WHITE, fontSize: 12.5 } },
    { text: "Perishability-aware dynamic pricing", options: { bullet: true, breakLine: true, color: WHITE, fontSize: 12.5 } },
    { text: "Real food-miles / carbon footprint scoring per order", options: { bullet: true, breakLine: true, color: WHITE, fontSize: 12.5 } },
    { text: "NLP quality-risk detection + subscription retention modeling", options: { bullet: true, color: WHITE, fontSize: 12.5 } },
  ], { x: 7.4, y: 2.7, w: 5.0, h: 3.6, valign: "top" });
  pageNum(s, 2);
}

// Slide 3 — Objectives grid
{
  let s = pres.addSlide();
  titleBar(s, "Scope", "Objectives — Brief + Research-Grade Extensions");
  const objs = [
    ["Marketplace Core", "Listings, inventory, browse/search, orders (brief requirement)"],
    ["Demand Forecasting", "Per-crop 14-day forecast from real price time series"],
    ["Dynamic Pricing", "Perishability-aware markdown optimization"],
    ["Farmer-Consumer Matching", "Distance + freshness + price-fit recommender"],
    ["Sustainability Scoring", "Real food-miles / CO2e per order"],
    ["Quality-Risk & Churn", "NLP review sentiment + subscription retention modeling"],
  ];
  const cols = 3, gw = 3.95, gh = 2.15, gx0 = 0.6, gy0 = 2.0, gap = 0.25;
  objs.forEach((o, i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const x = gx0 + col * (gw + gap), y = gy0 + row * (gh + gap);
    card(s, x, y, gw, gh);
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: y + 0.25, w: 0.5, h: 0.5, fill: { color: GREEN } });
    s.addText(String(i + 1), { x: x + 0.25, y: y + 0.25, w: 0.5, h: 0.5, align: "center", valign: "middle", fontSize: 16, bold: true, color: WHITE });
    s.addText(o[0], { x: x + 0.25, y: y + 0.9, w: gw - 0.5, h: 0.45, fontSize: 14, bold: true, color: NAVY, fontFace: "Calibri" });
    s.addText(o[1], { x: x + 0.25, y: y + 1.35, w: gw - 0.5, h: 0.7, fontSize: 10.5, color: SLATE, fontFace: "Calibri" });
  });
  pageNum(s, 3);
}

// Slide 4 — Architecture
{
  let s = pres.addSlide();
  titleBar(s, "System Design", "Target Azure Production Architecture");
  s.addImage({ path: "../architecture/architecture_diagram.png", x: 0.5, y: 1.6, w: 12.3, h: 5.5, sizing: { type: "contain", w: 12.3, h: 5.5 } });
  pageNum(s, 4);
}

// Slide 5 — Approved Azure services used
{
  let s = pres.addSlide();
  titleBar(s, "System Design", "Approved Azure Services Used");
  const rows = [
    [{ text: "Brief Requirement", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Azure Service", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Configuration (per program guidance)", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["App hosting", "Azure Virtual Machines (#1)", "B-series burstable, pay-as-you-go, deallocate when idle"],
    ["User & product data", "Azure SQL Database (#9)", "Basic / Serverless tier to minimize cost"],
    ["Image/document storage", "Azure Blob Storage (#8)", "Hot tier — real azure-storage-blob integration"],
    ["Event routing", "Azure Event Grid (#22)", "Basic tier, event-driven triggers"],
    ["Notifications & inventory automation", "Azure Functions (#11)", "Consumption plan, pay-per-execution"],
    ["Farmer-consumer communication", "Communication Services (#20) / Notification Hubs (#19)", "Free tier for push; note trial sending limits"],
    ["ML engines", "Azure Machine Learning (#26)", "Small compute instance, stop when idle"],
    ["Executive dashboards", "Power BI (#27)", "Power BI Desktop / free trial account"],
  ];
  s.addTable(rows, {
    x: 0.6, y: 1.75, w: 12.1, h: 4.9, fontSize: 10.8, fontFace: "Calibri", color: DARKTEXT,
    border: { pt: 0.75, color: "E2E4E7" }, autoPage: false, colW: [3.3, 3.7, 5.1],
  });
  s.addText("All services drawn directly from the program's approved Azure services list (AZ-900 aligned) — every objective and service role from the original brief is preserved.",
    { x: 0.6, y: 6.8, w: 12, h: 0.4, fontSize: 10.5, italic: true, color: SLATE });
  pageNum(s, 5);
}

// Slide 6 — Data honesty
{
  let s = pres.addSlide();
  titleBar(s, "Data", "Data Sources — What's Real, What's Simulated");
  const rows = [
    [{ text: "Data", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Source", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Used For", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["Vegetable prices\n(287 days x 10 crops, 2023)", "GitHub-mirrored Kaggle dataset", "Demand forecasting, pricing baseline"],
    ["Reviews\n(23,486 real ratings + text)", "GitHub-mirrored \"Women's Clothing\nE-Commerce Reviews\" — proxy dataset", "Sentiment/quality-risk NLP model validation"],
    ["Daily temperature\n(3,650 real days, Melbourne)", "GitHub-mirrored historical\nclimate station data", "Weather-driven harvest advisory"],
    ["Farmers, consumers, listings, orders", "Synthesized, grounded in real\nprice/seasonality structure", "Marketplace simulation & every downstream engine"],
  ];
  s.addTable(rows, {
    x: 0.6, y: 1.85, w: 12.1, h: 4.3, fontSize: 11.5, fontFace: "Calibri", color: DARKTEXT,
    border: { pt: 0.75, color: "E2E4E7" }, autoPage: false, colW: [3.4, 4.0, 4.7], valign: "middle",
  });
  card(s, 0.6, 6.3, 12.1, 0.85, LIGHT);
  s.addText("No public dataset ties real farms to real consumers. What's real is the underlying price, review, and climate structure — every synthesized entity is anchored to it, not arbitrary.",
    { x: 0.9, y: 6.4, w: 11.5, h: 0.65, fontSize: 10, color: DARKTEXT, italic: true, valign: "middle" });
  pageNum(s, 6);
}

// Slide 7 — Marketplace entities
{
  let s = pres.addSlide();
  titleBar(s, "Foundation", "Marketplace Universe");
  const stats = [["150", "Farmers"], ["800", "Consumers"], ["11,640", "Listings"], ["6,000", "Orders"], ["144", "Subscriptions"]];
  stats.forEach((st, i) => {
    const x = 0.6 + i * 2.46;
    card(s, x, 1.9, 2.3, 1.5);
    s.addText(st[0], { x, y: 2.05, w: 2.3, h: 0.7, align: "center", fontSize: 26, bold: true, color: GREEN, fontFace: "Cambria" });
    s.addText(st[1], { x, y: 2.75, w: 2.3, h: 0.5, align: "center", fontSize: 11, color: DARKTEXT });
  });

  s.addChart(pres.charts.BAR, [{
    name: "Orders", labels: ["Methi", "Tomato", "Onion", "Brinjal", "Potato", "Yam", "Bhindi", "Chilli", "Peas", "Garlic"],
    values: [1842, 1167, 659, 546, 521, 503, 472, 180, 107, 3],
  }], {
    x: 0.6, y: 3.7, w: 12.1, h: 3.1, barDir: "col", showTitle: true,
    title: "Orders by Crop — price-sensitive choice model correctly suppresses the priciest crop (Garlic)",
    chartColors: [GREEN], showValue: true, dataLabelPosition: "outEnd", showLegend: false,
    catAxisLabelColor: SLATE, valAxisLabelColor: SLATE, valGridLine: { color: "E2E4E7", size: 0.5 }, catGridLine: { style: "none" },
    chartArea: { fill: { color: WHITE } },
  });
  s.addText("Total GMV: $492,336  ·  Avg. delivery distance: 9.5 km  ·  Organic-certified farmers: 28%",
    { x: 0.6, y: 6.95, w: 12, h: 0.35, fontSize: 11, color: SLATE, italic: true });
  pageNum(s, 7);
}

// Slide 8 — Demand forecasting
{
  let s = pres.addSlide();
  titleBar(s, "Engine 1", "Demand Forecasting & Price Elasticity");
  s.addText("Price: OLS trend + day-of-week seasonality on the REAL 287-day price series. Elasticity: log-log regression on real transaction data — negative values confirm normal-good behavior (price up, demand down).",
    { x: 0.6, y: 1.7, w: 12.1, h: 0.7, fontSize: 12, color: SLATE });

  const rows = [
    [{ text: "Crop", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Current Price", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "14d Forecast", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Elasticity", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["Tomato", "$16.45", "$15.98", "-1.064"],
    ["Potato", "$19.46", "$21.07", "-1.014"],
    ["Brinjal", "$24.94", "$37.77", "-0.923"],
    ["Bhindi", "$25.52", "$29.08", "-0.882"],
    ["Onion", "$14.77", "$37.02", "-0.741"],
    ["Peas", "$31.25", "$92.90", "-0.691"],
    ["Methi", "$9.69", "$25.58", "-0.604"],
  ];
  s.addTable(rows, {
    x: 0.6, y: 2.55, w: 6.0, h: 4.0, fontSize: 11.5, fontFace: "Calibri", color: DARKTEXT,
    border: { pt: 0.75, color: "E2E4E7" }, autoPage: false, colW: [2.0, 1.4, 1.4, 1.2],
  });

  card(s, 6.9, 2.55, 5.8, 4.0, NAVY);
  s.addText("Reading the elasticities", { x: 7.2, y: 2.75, w: 5.2, h: 0.4, fontSize: 13.5, bold: true, color: GREEN });
  s.addText([
    { text: "Tomato (-1.06) is most elastic — small price moves swing demand sharply, so it's the best candidate for markdown-driven volume.", options: { breakLine: true, fontSize: 11.5, color: WHITE } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "Methi (-0.60) is least elastic here — demand holds up better under price increases.", options: { fontSize: 11.5, color: WHITE } },
  ], { x: 7.2, y: 3.25, w: 5.2, h: 3.0, valign: "top" });
  pageNum(s, 8);
}

// Slide 9 — Dynamic pricing
{
  let s = pres.addSlide();
  titleBar(s, "Engine 2", "Perishability-Aware Dynamic Pricing");
  s.addText("Markdown = base_decay(inventory age ÷ shelf life)³ × demand adjustment. Evaluated on live inventory only (last 10 days of listings), not the full historical log.",
    { x: 0.6, y: 1.7, w: 12.1, h: 0.6, fontSize: 12, color: SLATE });

  const stats = [["353", "Live listings priced"], ["19.5%", "Avg. markdown"], ["$961K", "Revenue at risk if unsold"]];
  stats.forEach((st, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 2.4, 3.85, 1.4, NAVY);
    s.addText(st[0], { x, y: 2.55, w: 3.85, h: 0.65, align: "center", fontSize: 28, bold: true, color: GREEN, fontFace: "Cambria" });
    s.addText(st[1], { x, y: 3.2, w: 3.85, h: 0.5, align: "center", fontSize: 11, color: WHITE });
  });

  card(s, 0.6, 4.0, 12.1, 2.8);
  s.addText("Why a convex (cubed) markdown curve?", { x: 0.9, y: 4.15, w: 8, h: 0.4, fontSize: 13, bold: true, color: NAVY });
  s.addText("Negligible discount in the first half of shelf life, then a steep ramp near expiry — the same shape used in retail \"reduced to clear\" markdown practice. Demand-forecast signal from Engine 1 scales the markdown up when forecasted demand is weak, down (or to a small premium) when it's strong, so pricing responds to both freshness AND market conditions, not freshness alone.",
    { x: 0.9, y: 4.6, w: 11.3, h: 2.0, fontSize: 11.5, color: DARKTEXT, valign: "top" });
  pageNum(s, 9);
}

// Slide 10 — Matching
{
  let s = pres.addSlide();
  titleBar(s, "Engine 3", "Farmer–Consumer Matching");
  s.addText("Weighted score: 30% freshness + 30% price-fit (vs. that crop's real market price) + 30% distance + 10% organic-match bonus for sustainability-conscious consumers.",
    { x: 0.6, y: 1.75, w: 12.1, h: 0.7, fontSize: 12.5, color: SLATE });

  const examples = [
    ["CONS-0061", "Onion (score 0.871, 19.3km, 97% fresh, $7.57)"],
    ["CONS-0799", "Elephant Yam (score 0.871, 28.6km, 89% fresh, $23.68)"],
    ["CONS-0747", "Onion (score 0.891, 16.8km, 100% fresh, $7.45)"],
  ];
  let y = 2.8;
  examples.forEach((row) => {
    card(s, 0.6, y, 12.1, 1.1);
    s.addText(row[0], { x: 0.9, y: y + 0.15, w: 2.2, h: 0.4, fontSize: 13, bold: true, color: NAVY });
    s.addText("Top match: " + row[1], { x: 0.9, y: y + 0.55, w: 10.5, h: 0.4, fontSize: 11.5, color: DARKTEXT });
    y += 1.3;
  });
  pageNum(s, 10);
}

// Slide 11 — Sustainability
{
  let s = pres.addSlide();
  titleBar(s, "Engine 4", "Sustainability & Food-Miles Impact");
  s.addChart(pres.charts.BAR, [
    { name: "Emissions (kg CO2e)", labels: ["This marketplace\n(local delivery)", "Conventional\nsupply chain"], values: [31.0, 2818.1] },
  ], {
    x: 0.6, y: 1.85, w: 6.6, h: 4.6, barDir: "col", showTitle: true, title: "Total Emissions Comparison",
    chartColors: [GREEN], showValue: true, dataLabelPosition: "outEnd", showLegend: false,
    catAxisLabelColor: SLATE, valAxisLabelColor: SLATE, valGridLine: { color: "E2E4E7", size: 0.5 }, catGridLine: { style: "none" },
    chartArea: { fill: { color: WHITE } },
  });

  card(s, 7.5, 1.85, 5.2, 4.6, GREEN);
  s.addText("98.9%", { x: 7.8, y: 2.1, w: 4.6, h: 1.1, fontSize: 46, bold: true, color: WHITE, fontFace: "Cambria" });
  s.addText("average emissions reduction per order vs. conventional supply chain", { x: 7.8, y: 3.15, w: 4.6, h: 0.7, fontSize: 12.5, color: WHITE });
  s.addText([
    { text: "Methodology (stated, not hidden):", options: { breakLine: true, bold: true, fontSize: 11.5, color: WHITE } },
    { text: "0.12 kg CO2e/tonne-km emission factor (published mid-range estimate)", options: { bullet: true, breakLine: true, fontSize: 10.5, color: WHITE } },
    { text: "800 km conventional baseline distance (conservative)", options: { bullet: true, breakLine: true, fontSize: 10.5, color: WHITE } },
    { text: "8 kg CO2e/tonne cold-storage overhead avoided", options: { bullet: true, fontSize: 10.5, color: WHITE } },
  ], { x: 7.8, y: 4.1, w: 4.6, h: 2.2, valign: "top" });
  pageNum(s, 11);
}

// Slide 12 — Review sentiment
{
  let s = pres.addSlide();
  titleBar(s, "Engine 5", "Review Sentiment & Quality-Risk (NLP)");
  const stats = [["90.9%", "Accuracy (real data)"], ["0.960", "ROC-AUC (real data)"], ["28 / 106", "Farmers flagged quality-risk"]];
  stats.forEach((st, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.9, 3.85, 1.5, NAVY);
    s.addText(st[0], { x, y: 2.05, w: 3.85, h: 0.7, align: "center", fontSize: 28, bold: true, color: GREEN, fontFace: "Cambria" });
    s.addText(st[1], { x, y: 2.75, w: 3.85, h: 0.5, align: "center", fontSize: 11, color: WHITE });
  });

  card(s, 0.6, 3.65, 12.1, 3.1);
  s.addText("Two-stage, honestly-scoped pipeline", { x: 0.9, y: 3.8, w: 11.3, h: 0.4, fontSize: 13.5, bold: true, color: NAVY });
  s.addText([
    { text: "1. Validate:", options: { bold: true, breakLine: true, fontSize: 12, color: NAVY } },
    { text: "TF-IDF + Logistic Regression trained on 23,486 REAL ratings+text reviews (train/test 15,854/3,964) — 90.9% accuracy, 0.960 ROC-AUC.", options: { breakLine: true, fontSize: 11.5, color: DARKTEXT } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "2. Apply:", options: { bold: true, breakLine: true, fontSize: 12, color: NAVY } },
    { text: "The validated model scores synthetic marketplace reviews (text templates weighted by each farmer's real organic/experience quality signal), flagging farmers whose average predicted sentiment falls below 0.4 with 3+ reviews.", options: { fontSize: 11.5, color: DARKTEXT } },
  ], { x: 0.9, y: 4.25, w: 11.3, h: 2.4, valign: "top" });
  pageNum(s, 12);
}

// Slide 13 — Subscription churn
{
  let s = pres.addSlide();
  titleBar(s, "Engine 6", "Subscription Retention Modeling");
  s.addText("N=144 subscriptions — too small for a single train/test split to give a stable estimate, so we used 5-fold cross-validated logistic regression instead of an overfit gradient-boosted model (which scored WORSE than random on the first attempt — reported honestly, not hidden).",
    { x: 0.6, y: 1.75, w: 12.1, h: 0.9, fontSize: 12, color: SLATE });

  const stats = [["0.576", "CV Accuracy"], ["0.577", "CV ROC-AUC"], ["90 / 144", "Currently active"]];
  stats.forEach((st, i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 2.75, 3.85, 1.3, NAVY);
    s.addText(st[0], { x, y: 2.85, w: 3.85, h: 0.6, align: "center", fontSize: 24, bold: true, color: GREEN, fontFace: "Cambria" });
    s.addText(st[1], { x, y: 3.45, w: 3.85, h: 0.5, align: "center", fontSize: 11, color: WHITE });
  });

  s.addChart(pres.charts.BAR, [{
    name: "Standardized coefficient",
    labels: ["Box Value", "Price\nSensitivity", "Frequency", "Tenure\n(days)"],
    values: [0.357, 0.268, 0.202, -0.021],
  }], {
    x: 0.6, y: 4.3, w: 12.1, h: 2.5, barDir: "bar", showTitle: true,
    title: "Churn Drivers (logistic regression coefficients — correctly signed vs. the generative model)",
    chartColors: [GREEN], showValue: true, dataLabelPosition: "outEnd", showLegend: false,
    catAxisLabelColor: SLATE, valAxisLabelColor: SLATE, valGridLine: { color: "E2E4E7", size: 0.5 }, catGridLine: { style: "none" },
    chartArea: { fill: { color: WHITE } },
  });
  pageNum(s, 13);
}

// Slide 14 — Weather advisory + A/B testing combined
{
  let s = pres.addSlide();
  titleBar(s, "Engines 7 & 8", "Weather Advisory & A/B Testing");
  card(s, 0.6, 1.9, 5.9, 4.6);
  s.addText("Weather-Driven Harvest Advisory", { x: 0.9, y: 2.1, w: 5.3, h: 0.4, fontSize: 14, bold: true, color: NAVY });
  s.addText([
    { text: "Real 10-year daily temperature series x standard crop temperature ranges.", options: { breakLine: true, fontSize: 11.5, color: DARKTEXT } },
    { text: " ", options: { breakLine: true, fontSize: 6 } },
    { text: "Peas: 91.6% suitability in December", options: { bullet: true, breakLine: true, fontSize: 11, color: DARKTEXT } },
    { text: "Garlic: 90.4% suitability in February", options: { bullet: true, breakLine: true, fontSize: 11, color: DARKTEXT } },
    { text: "Onion: 84.0% suitability in February", options: { bullet: true, breakLine: true, fontSize: 11, color: DARKTEXT } },
    { text: "Bhindi: <2% year-round (needs 24-35°C — genuinely a poor climate match, reported honestly)", options: { bullet: true, fontSize: 11, color: DARKTEXT } },
  ], { x: 0.9, y: 2.6, w: 5.3, h: 3.7, valign: "top" });

  card(s, 6.8, 1.9, 5.9, 4.6, NAVY);
  s.addText("A/B Test: Organic vs. Non-Organic", { x: 7.1, y: 2.1, w: 5.3, h: 0.4, fontSize: 14, bold: true, color: GREEN });
  s.addText([
    { text: "Non-organic conversion: 31.4%", options: { breakLine: true, fontSize: 12.5, color: WHITE } },
    { text: "Organic conversion: 22.9%  (-27.3% lift)", options: { breakLine: true, fontSize: 12.5, color: WHITE } },
    { text: "p < 0.001, Bayesian P(organic wins) = 0.00", options: { breakLine: true, fontSize: 12.5, color: WHITE } },
    { text: " ", options: { breakLine: true, fontSize: 8 } },
    { text: "Real, slightly counterintuitive finding: the 12% organic price premium outweighs quality preference for this consumer base — price sensitivity dominates. Framework is fully reusable for any future test.", options: { fontSize: 11.5, color: WHITE } },
  ], { x: 7.1, y: 2.6, w: 5.3, h: 3.7, valign: "top" });
  pageNum(s, 14);
}

// Slide 15 — Dashboard
{
  let s = pres.addSlide();
  titleBar(s, "Delivery", "Streamlit Operations Dashboard");
  s.addText("12 tabs unifying every engine into one live, explorable platform:",
    { x: 0.6, y: 1.75, w: 12, h: 0.4, fontSize: 13, color: SLATE });
  const tabItems = ["Overview & KPIs", "Farmers & Listings", "Orders & GMV", "Demand Forecast",
    "Dynamic Pricing", "Matching", "Sustainability", "Reviews & Quality",
    "Subscriptions", "Weather Advisory", "A/B Testing", "Architecture"];
  const cols = 4, gw = 2.95, gh = 1.05, gx0 = 0.6, gy0 = 2.3, gap = 0.2;
  tabItems.forEach((t, i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const x = gx0 + col * (gw + gap), y = gy0 + row * (gh + gap);
    card(s, x, y, gw, gh);
    s.addText(t, { x: x + 0.15, y, w: gw - 0.3, h: gh, valign: "middle", fontSize: 12, bold: true, color: NAVY });
  });
  pageNum(s, 15);
}

// Slide 16 — Closing
{
  let s = pres.addSlide();
  s.background = { color: NAVY };
  s.addText("Thank You", { x: 0.8, y: 2.6, w: 8, h: 1.2, fontSize: 44, bold: true, color: WHITE, fontFace: "Cambria" });
  s.addText("Repository, engines, and dashboard available for live demo.", { x: 0.8, y: 3.7, w: 9, h: 0.5, fontSize: 14, color: "CBD3DC" });
  s.addText("AgriConnect  ·  P14  ·  VIT–Azure Internship (AZ-900)", { x: 0.8, y: 6.6, w: 8, h: 0.4, fontSize: 12, bold: true, color: GREEN });
  pageNum(s, 16);
}

pres.writeFile({ fileName: "AgriConnect_P14.pptx" }).then(() => console.log("done"));
