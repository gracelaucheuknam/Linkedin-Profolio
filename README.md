# 📊 E-Commerce Analytics Dashboard

> **Interactive data analytics portfolio** — built to demonstrate end-to-end analytical thinking, from raw SQL to actionable business insights.

[![Live Demo](https://img.shields.io/badge/Live_Demo-▶_Open_Dashboard-378ADD?style=for-the-badge)](https://your-username.github.io/ecommerce-analytics-dashboard)
[![Made with](https://img.shields.io/badge/Made_with-HTML_·_Chart.js_·_Vanilla_JS-1D9E75?style=for-the-badge)](#)
[![Skills](https://img.shields.io/badge/Skills-SQL_·_Python_·_Forecasting_·_Cohort_Analysis-7F77DD?style=for-the-badge)](#)

---

## 🗂️ What's inside

| Section | What it shows |
|---|---|
| **Overview** | KPI dashboard with region & category filters, cohort retention heatmap, conversion funnel |
| **Forecast** | Revenue forecasting with 3 models (Linear / Exponential / Seasonal), scenario comparison, backtesting |
| **SQL Explorer** | 5 production-grade queries with syntax highlighting and simulated execution — RFM, cohort, funnel, margin |

---

## 🏗️ Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA PIPELINE OVERVIEW                           │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │  Data Source │    │  Data Source │    │  Data Source │
  │              │    │              │    │              │
  │  Orders DB   │    │  Sessions    │    │  Product     │
  │  (Postgres)  │    │  (Clickhouse)│    │  Catalogue   │
  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                   ┌──────────────────┐
                   │   ETL / dbt      │
                   │                  │
                   │  • Incremental   │
                   │    loads         │
                   │  • Data quality  │
                   │    tests         │
                   │  • Mart models   │
                   └────────┬─────────┘
                            │
               ┌────────────┼─────────────┐
               │            │             │
               ▼            ▼             ▼
     ┌──────────────┐ ┌──────────┐ ┌──────────────┐
     │  mart_orders │ │mart_cust │ │mart_sessions │
     │              │ │omers     │ │              │
     │  revenue     │ │          │ │  funnel      │
     │  margin      │ │  LTV     │ │  CVR         │
     │  region      │ │  cohort  │ │  source      │
     └──────┬───────┘ └────┬─────┘ └──────┬───────┘
            │              │              │
            └──────────────┼──────────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │    Analysis Layer     │
               │                       │
               │  SQL  ─────────────── │──► KPI aggregations
               │  Python ────────────  │──► Forecasting models
               │  Window functions ──  │──► Cohort retention
               │  RFM scoring ───────  │──► Customer segments
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │   Visualisation       │
               │                       │
               │  Chart.js charts      │
               │  Interactive filters  │
               │  Forecast bands       │
               │  SQL Explorer         │
               └───────────────────────┘
```

---

## 💡 Key Insights

### 1 · APAC is the growth engine
APAC posted **+24.1% YoY revenue growth** — outpacing EMEA (+15%) and Americas (+12%). Yet APAC's share of total orders only grew 3pp, meaning the real driver is a rising average order value ($113 vs global average $109). **Recommendation:** prioritise APAC checkout localisation and premium SKU expansion.

### 2 · Cart abandonment is a $380K opportunity
The conversion funnel shows 96,000 sessions add to cart but only 63,000 reach checkout — a **34% step-level drop**, the single biggest leak in the funnel. An A/B test on checkout UX reduced this by 8pp in Q4. Extrapolating to full-year volume implies **~$380K recoverable revenue** from closing this gap.

### 3 · Retention improved — and we know exactly why
M1 cohort retention climbed from **68% (Jan cohort) → 74% (May cohort)** after the onboarding email redesign shipped in April. No other variable changed in that window. Each 1pp gain in M1 retention compounds across 12 months of purchase cycles — targeting 75% by Q1 2025 is achievable and high-ROI.

### 4 · Champions drive disproportionate revenue
RFM segmentation reveals that **Champions (18% of customers) contribute 52% of total revenue** at an average LTV of $458. The "At Risk" segment holds 2,412 customers with $318 average LTV — a **$768K retention priority** if churn can be reversed with a targeted win-back campaign.

### 5 · Yoga Mat Pro is the hidden margin star
Despite ranking #4 by revenue, Yoga Mat Pro carries a **64% gross margin** — the highest in the portfolio, vs 38% for the top-revenue ProBook Air. A pricing or bundling strategy that shifts even 5% of electronics revenue to Home & Garden could meaningfully improve overall blended margins.

### 6 · Seasonal decomposition outperforms simple linear forecasting
Backtesting shows the seasonal model achieves **MAPE 4.2%** vs 7.8% for linear — particularly strong in Q4 where linear models underestimate holiday uplift by ~12%. For FY2025 planning, seasonal decomposition with +2%/month base growth projects **$5.1M annual revenue** (95% CI: $4.8M–$5.4M).

---

## 🛠️ Technical skills demonstrated

```
SQL                     ████████████████████  Window functions, CTEs, NTILE, LAG
Python / Forecasting    ████████████████░░░░  Time series, seasonal decomp, backtesting
Data Visualisation      ████████████████████  Chart.js, interactive filters, custom legends
Cohort Analysis         ███████████████░░░░░  M0–M6 retention, heatmap rendering
RFM Segmentation        ████████████████░░░░  Recency / Frequency / Monetary scoring
A/B Testing             █████████████░░░░░░░  Funnel analysis, uplift measurement
```

---

## 🚀 Run locally

```bash
# Clone the repo
git clone https://github.com/your-username/ecommerce-analytics-dashboard.git
cd ecommerce-analytics-dashboard

# Open directly in browser — no build step needed
open analytics_dashboard.html
# or: python -m http.server 8000 → localhost:8000
```

---

## 📁 File structure

```
ecommerce-analytics-dashboard/
├── analytics_dashboard.html   # Single-file interactive dashboard
├── README.md                  # This file
└── slides/
    └── data_story.pdf         # LinkedIn carousel deck
```

---

## 📬 Contact

Built by a data analyst who believes **good analysis tells a story, not just a number**.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat-square&logo=linkedin)](https://linkedin.com/in/your-profile)
[![Email](https://img.shields.io/badge/Email-Say_hello-D85A30?style=flat-square)](mailto:your@email.com)
