# Macro Economic Data API

Live database of macroeconomic indicators focused on copper/gold ratio analysis.

## 🔗 API Access

**JSON Endpoint**: `macro_data_api.json`

```javascript
// Fetch the data
fetch('https://[YOUR-USERNAME].github.io/[REPO-NAME]/macro_data_api.json')
  .then(r => r.json())
  .then(data => console.log(data))
```

## 📊 Dashboard

View the interactive dashboard: `macro_dashboard.html`

API documentation: `macro_data_api.html`

## 📈 Data Included

- **39 Economic Indicators** from FRED and Yahoo Finance
- **Current Values** for quick access
- **Historical Data** (last 30 points per indicator)
- **Statistics** (mean, min, max, std deviation)
- **Correlations** including the key 0.845 correlation (Cu/Au vs Manufacturing with 6-month lead)
- **Thesis Summary** with predictions and historical precedents

## 🎯 Key Insights

- **Copper/Gold Ratio**: Currently at 0.001262 (50-year lows)
- **Leading Indicator**: Cu/Au leads manufacturing by 6 months (0.845 correlation)
- **Bitcoin Cycle Timing**: Cu/Au peaks preceded BTC tops by 12-60 days in 2013, 2017, 2021
- **Current Signal**: Early in risk cycle, not late

## 📊 Available Charts

### Main Analysis Charts:
1. `copper_gold_ratio_PROPER.png` - Full history with proper units
2. `copper_price_per_lb.png` - Copper in USD/lb
3. `gold_price_per_oz.png` - Gold in USD/oz

### Thesis Charts (For Articles):
1. `thesis_chart1_copper_gold_leads_ism.png` - 6-month lead relationship ⭐
2. `thesis_chart2_copper_gold_vs_sp500.png` - Risk appetite correlation
3. `thesis_chart3_copper_gold_vs_bitcoin.png` - Crypto cycle timing
4. `thesis_chart4_liquidity_dashboard.png` - 4-panel liquidity indicators
5. `thesis_chart5_copper_gold_vs_dollar.png` - Dollar inverse relationship

## 🔄 Updating the Data

Run these scripts to refresh the data:

```bash
# Update all data
python3 macro_database.py

# Regenerate API export
python3 export_data_api.py

# Update charts
python3 regenerate_all_charts.py
```

## 💬 Using with Claude

Tell Claude to fetch your data:

```
Fetch and analyze the macro data from https://[YOUR-USERNAME].github.io/[REPO-NAME]/macro_data_api.json
```

Claude will have access to all 39 indicators, current values, correlations, and the thesis summary.

## 📖 Reference Documents

- `ARTICLE_BRIEF.md` - Comprehensive thesis and data points for article writing
- `CHART_REFERENCE.txt` - Quick reference for chart interpretations
- `HOW_TO_USE_WITH_CLAUDE.md` - Guide for using this data with Claude chat

## 🛠️ Technical Details

- **Data Sources**: Federal Reserve Economic Data (FRED), Yahoo Finance
- **Database**: SQLite with pandas integration
- **Visualization**: Matplotlib with proper datetime handling
- **API Format**: JSON with nested structure for easy querying
- **Update Frequency**: Manual refresh (run scripts as needed)

## 📊 Indicator Categories

- **Metals**: Copper, Gold, Cu/Au Ratio
- **Liquidity**: SOFR, Fed Funds Rate, M2, Fed Balance Sheet, Reverse Repo
- **Credit**: High Yield Spreads, Investment Grade Spreads
- **Treasuries**: 2Y, 5Y, 10Y, TIPS, Breakevens
- **Equities**: S&P 500, NASDAQ, VIX
- **Manufacturing**: Industrial Production, Employment, Capacity Utilization
- **Currency**: Dollar Index (DXY)
- **Commodities**: Oil, Bitcoin
- **Sentiment**: University of Michigan Consumer Sentiment

---

**Last Updated**: Check the `last_updated` field in `macro_data_api.json`

**License**: Data sourced from public APIs (FRED, Yahoo Finance)
