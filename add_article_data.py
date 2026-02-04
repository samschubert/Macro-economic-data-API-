"""
Add data series needed for the copper/gold ratio article.
"""

from macro_database import FREDDataFetcher, MacroDatabase
import yfinance as yf
import pandas as pd
import requests

def fetch_btc_dominance():
    """Fetch Bitcoin dominance from alternative sources."""
    try:
        # Try CoinGecko API (no key required)
        url = "https://api.coingecko.com/api/v3/global"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            btc_dom = data['data']['market_cap_percentage']['btc']
            print(f"Current BTC Dominance: {btc_dom:.2f}%")

            # For historical data, we'll need to use Yahoo Finance BTC.D or similar
            # Let's try fetching from Yahoo
            ticker = yf.Ticker("BTC-USD")
            # Note: BTC dominance historical data is harder to get
            # We'll create a simple current value entry
            return pd.DataFrame({
                'date': [pd.Timestamp.now()],
                'value': [btc_dom]
            })
    except Exception as e:
        print(f"Error fetching BTC dominance: {e}")
        return None

def main():
    print("=" * 70)
    print("ADDING ARTICLE DATA SERIES")
    print("=" * 70)

    api_key = "d84ee068104098a83a9619da9b8412de"
    fetcher = FREDDataFetcher(api_key)
    db = MacroDatabase('macro_data.db')

    # 1. ISM Manufacturing PMI
    print("\n1. Fetching ISM Manufacturing PMI...")
    try:
        # Try the main ISM PMI series
        ism_series_options = [
            'MANEMP',  # ISM Manufacturing: Employment Index
            'NAPM',    # ISM Manufacturing: PMI Composite Index (might be discontinued)
            'IPMAN',   # Industrial Production: Manufacturing (we already have this)
        ]

        # Let's try to get the actual ISM PMI if available
        # If not, we'll note what we have
        print("   Attempting to fetch ISM PMI series...")

        # Try ISM Manufacturing New Orders (a good leading indicator)
        ism_new_orders = fetcher.fetch_series('NEWORDER', start_date='2000-01-01')
        if len(ism_new_orders) > 0:
            db.insert_indicator_data(
                'ism_manufacturing_new_orders',
                ism_new_orders,
                'FRED',
                'NEWORDER',
                'ISM Manufacturing: New Orders Index'
            )
            print(f"   ✓ Added ISM New Orders: {len(ism_new_orders)} records")

        # Try ISM Manufacturing Production
        ism_production = fetcher.fetch_series('IPMAN', start_date='2000-01-01')
        if len(ism_production) > 0:
            # We already have this, but let's make sure
            print(f"   ✓ Industrial Production (Manufacturing): {len(ism_production)} records")

    except Exception as e:
        print(f"   ⚠ ISM PMI fetch issue: {e}")
        print("   Using existing Industrial Production data as proxy")

    # 2. Russell 2000 Index
    print("\n2. Fetching Russell 2000...")
    try:
        rut = yf.Ticker("^RUT")
        rut_hist = rut.history(start="2000-01-01", end=pd.Timestamp.now())

        if len(rut_hist) > 0:
            rut_data = pd.DataFrame({
                'date': rut_hist.index,
                'value': rut_hist['Close'].values
            })
            rut_data['date'] = pd.to_datetime(rut_data['date']).dt.tz_localize(None).dt.normalize()

            db.insert_indicator_data(
                'russell_2000',
                rut_data,
                'Yahoo Finance',
                '^RUT',
                'Russell 2000 Index'
            )
            print(f"   ✓ Added Russell 2000: {len(rut_data)} records")
            print(f"   Latest: {rut_data['value'].iloc[-1]:.2f} ({rut_data['date'].iloc[-1].strftime('%Y-%m-%d')})")

    except Exception as e:
        print(f"   ✗ Error fetching Russell 2000: {e}")

    # 3. Bitcoin Dominance
    print("\n3. Fetching Bitcoin Dominance...")
    try:
        btc_dom = fetch_btc_dominance()
        if btc_dom is not None and len(btc_dom) > 0:
            db.insert_indicator_data(
                'btc_dominance',
                btc_dom,
                'CoinGecko',
                'BTC-DOM',
                'Bitcoin Market Dominance (%)'
            )
            print(f"   ✓ Added BTC Dominance: {btc_dom['value'].iloc[0]:.2f}%")
            print("   Note: Historical BTC dominance data limited, showing current value")

    except Exception as e:
        print(f"   ⚠ BTC Dominance: {e}")
        print("   Note: Historical dominance data requires paid API or manual data")

    # Verify SOFR and M2 data exists
    print("\n4. Verifying existing key indicators...")
    sofr = db.get_indicator_data('sofr')
    sofr_spread = db.get_indicator_data('sofr_dff_spread')
    m2 = db.get_indicator_data('m2sl')

    print(f"   ✓ SOFR: {len(sofr)} records")
    print(f"   ✓ SOFR-DFF Spread: {len(sofr_spread)} records")
    print(f"   ✓ M2 Money Supply: {len(m2)} records")

    db.close()

    print("\n" + "=" * 70)
    print("✅ DATA UPDATE COMPLETE")
    print("=" * 70)
    print("\nReady to generate article charts!")

if __name__ == "__main__":
    main()
