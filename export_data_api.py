"""
Export database to JSON format for API access.
Creates a structured JSON file that Claude can reference.
"""

from macro_database import MacroDatabase
import json
from datetime import datetime


def export_to_json():
    """Export all data to structured JSON."""
    print("📊 Exporting database to JSON API format...")

    db = MacroDatabase('macro_data.db')

    # Main data structure
    api_data = {
        "last_updated": datetime.now().isoformat(),
        "metadata": {
            "total_indicators": 0,
            "date_range": {},
            "description": "Macro economic indicators database for copper/gold ratio analysis"
        },
        "current_values": {},
        "indicators": {},
        "correlations": {},
        "thesis": {}
    }

    # Get list of all indicators
    cursor = db.conn.cursor()
    cursor.execute("""
        SELECT DISTINCT indicator_name
        FROM macro_indicators
        ORDER BY indicator_name
    """)
    indicators = [row[0] for row in cursor.fetchall()]
    api_data["metadata"]["total_indicators"] = len(indicators)

    print(f"Found {len(indicators)} indicators")

    # Export each indicator
    for indicator in indicators:
        print(f"  Exporting {indicator}...")
        data = db.get_indicator_data(indicator)

        if len(data) == 0:
            continue

        # Get metadata
        cursor.execute("""
            SELECT description, source, series_id
            FROM indicator_metadata
            WHERE indicator_name = ?
        """, (indicator,))
        meta = cursor.fetchone()

        # Store data
        api_data["indicators"][indicator] = {
            "description": meta[0] if meta else "",
            "source": meta[1] if meta else "",
            "series_id": meta[2] if meta else "",
            "records": len(data),
            "date_range": {
                "start": data['date'].min().strftime('%Y-%m-%d'),
                "end": data['date'].max().strftime('%Y-%m-%d')
            },
            "latest_value": float(data['value'].iloc[-1]),
            "latest_date": data['date'].iloc[-1].strftime('%Y-%m-%d'),
            "statistics": {
                "mean": float(data['value'].mean()),
                "min": float(data['value'].min()),
                "max": float(data['value'].max()),
                "std": float(data['value'].std())
            },
            "recent_data": [
                {
                    "date": row['date'].strftime('%Y-%m-%d'),
                    "value": float(row['value'])
                }
                for _, row in data.tail(30).iterrows()
            ]
        }

        # Add to current values for quick access
        api_data["current_values"][indicator] = {
            "value": float(data['value'].iloc[-1]),
            "date": data['date'].iloc[-1].strftime('%Y-%m-%d')
        }

    # Add key correlations
    api_data["correlations"] = {
        "copper_gold_vs_manufacturing": {
            "no_shift": 0.518,
            "six_month_forward_shift": 0.845,
            "description": "Cu/Au ratio vs Industrial Production"
        },
        "copper_gold_vs_sp500": {
            "correlation": "strong_positive",
            "description": "Cu/Au ratio tracks equity risk appetite"
        }
    }

    # Add thesis summary
    api_data["thesis"] = {
        "title": "Copper/Gold at 50-Year Lows: Major Risk-On Signal",
        "key_points": [
            "Cu/Au ratio at 0.001262 (50-year lows)",
            "Historical 6-month lead on manufacturing (0.845 correlation)",
            "All liquidity indicators turning positive",
            "BTC cycle timing suggests early phase, not late",
            "Dollar weakness adds fuel to risk-on trade"
        ],
        "predicted_timeline": {
            "manufacturing_acceleration": "Q2-Q3 2026",
            "risk_asset_rally": "Next 3-6 months",
            "btc_cycle_peak_signal": "Cu/Au peaks will precede by 12-60 days"
        },
        "historical_precedent": {
            "btc_2013": "Cu/Au peak preceded BTC top by ~60 days",
            "btc_2017": "Cu/Au peak preceded BTC top by ~30 days",
            "btc_2021": "Cu/Au peak preceded BTC top by ~12 days"
        }
    }

    # Write to JSON file
    with open('macro_data_api.json', 'w') as f:
        json.dump(api_data, f, indent=2)

    print(f"\n✅ Exported to macro_data_api.json")
    print(f"   File size: {len(json.dumps(api_data)) / 1024:.1f} KB")

    db.close()

    return api_data


def create_simple_api_html():
    """Create a simple HTML page that displays the data."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Macro Data API</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: 'Courier New', monospace;
            max-width: 1200px;
            margin: 40px auto;
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        h1 { color: #4fc3f7; }
        h2 { color: #81c784; margin-top: 30px; }
        .endpoint {
            background: #2d2d2d;
            border-left: 4px solid #4fc3f7;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .value {
            color: #ce93d8;
            font-weight: bold;
        }
        pre {
            background: #2d2d2d;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
        code { color: #f48fb1; }
        a { color: #4fc3f7; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .stat { margin: 10px 0; }
    </style>
</head>
<body>
    <h1>📊 Macro Economic Data API</h1>
    <p>Live database for copper/gold ratio analysis and macro indicators</p>

    <h2>🔗 API Endpoint</h2>
    <div class="endpoint">
        <strong>GET</strong> <code>/macro_data_api.json</code>
        <p>Returns all indicators, current values, correlations, and thesis data</p>
    </div>

    <h2>📈 Current Key Values</h2>
    <div id="current-values">Loading...</div>

    <h2>💡 Thesis Summary</h2>
    <div id="thesis">Loading...</div>

    <h2>📊 Available Indicators</h2>
    <div id="indicators">Loading...</div>

    <h2>🔗 Charts</h2>
    <ul>
        <li><a href="thesis_chart1_copper_gold_leads_ism.png">Chart 1: Cu/Au Leads Manufacturing (6mo)</a></li>
        <li><a href="thesis_chart2_copper_gold_vs_sp500.png">Chart 2: Cu/Au vs S&P 500</a></li>
        <li><a href="thesis_chart3_copper_gold_vs_bitcoin.png">Chart 3: Cu/Au vs Bitcoin Cycles</a></li>
        <li><a href="thesis_chart4_liquidity_dashboard.png">Chart 4: Liquidity Dashboard</a></li>
        <li><a href="thesis_chart5_copper_gold_vs_dollar.png">Chart 5: Cu/Au vs Dollar</a></li>
    </ul>

    <h2>📖 Usage for Claude</h2>
    <pre>
# Tell Claude:
"Fetch the data from [YOUR_URL]/macro_data_api.json and analyze it"

# Or reference specific indicators:
"Look at the copper_gold_ratio_proper indicator in the API"

# For article writing:
"Use the thesis section and current values to write about the 50-year lows"
    </pre>

    <script>
        fetch('macro_data_api.json')
            .then(r => r.json())
            .then(data => {
                // Display current values
                const cvDiv = document.getElementById('current-values');
                const key_indicators = ['copper_gold_ratio_proper', 'bitcoin_price', 'sp500', 'dtwexbgs'];
                let cvHtml = '';
                for (const ind of key_indicators) {
                    if (data.current_values[ind]) {
                        cvHtml += `<div class="stat">${ind}: <span class="value">${data.current_values[ind].value.toFixed(6)}</span> (${data.current_values[ind].date})</div>`;
                    }
                }
                cvDiv.innerHTML = cvHtml;

                // Display thesis
                const thesisDiv = document.getElementById('thesis');
                let thesisHtml = `<p><strong>${data.thesis.title}</strong></p><ul>`;
                data.thesis.key_points.forEach(point => {
                    thesisHtml += `<li>${point}</li>`;
                });
                thesisHtml += '</ul>';
                thesisDiv.innerHTML = thesisHtml;

                // Display indicators
                const indDiv = document.getElementById('indicators');
                indDiv.innerHTML = `<p>Total: <span class="value">${data.metadata.total_indicators}</span> indicators available</p>`;
            })
            .catch(e => console.error(e));
    </script>
</body>
</html>
"""

    with open('macro_data_api.html', 'w') as f:
        f.write(html)

    print("✅ Created macro_data_api.html")


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 CREATING LIVE DATA API")
    print("=" * 70)

    export_to_json()
    create_simple_api_html()

    print("\n" + "=" * 70)
    print("✅ API READY")
    print("=" * 70)
    print("\nFiles created:")
    print("  • macro_data_api.json - All data in JSON format")
    print("  • macro_data_api.html - API documentation page")
    print("\nNext steps:")
    print("  1. Host these files on GitHub Pages / Netlify / Vercel")
    print("  2. Get public URL (e.g., https://yourname.github.io/macro-data/)")
    print("  3. Tell Claude: 'Fetch data from [URL]/macro_data_api.json'")
    print("\nClaude will then have live access to all your data!")
    print("=" * 70)
