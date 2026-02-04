"""
Add Real Vision-inspired data series to the macro database.
Based on analysis of Real Vision PDFs (Business Cycle Update & Commodity Season).
"""

from macro_database import FREDDataFetcher, MacroDatabase
import yfinance as yf
import pandas as pd
import numpy as np

def calculate_yoy_percent(series):
    """Calculate year-over-year percentage change."""
    return series.pct_change(periods=252).dropna() * 100  # 252 trading days ≈ 1 year

def calculate_3mo3m_percent(series):
    """Calculate 3-month over 3-month percentage change."""
    return series.pct_change(periods=63).dropna() * 100  # ~63 trading days = 3 months

def main():
    print("=" * 70)
    print("ADDING REAL VISION DATA SERIES")
    print("=" * 70)

    api_key = "d84ee068104098a83a9619da9b8412de"
    fetcher = FREDDataFetcher(api_key)
    db = MacroDatabase('macro_data.db')

    # 1. Taiwan Exports (leads ISM for AI/semiconductor cycle)
    print("\n1. Fetching Taiwan Exports...")
    try:
        # FRED series for Taiwan exports
        taiwan_exports = fetcher.fetch_series('XTEXVA01TWM667S', start_date='2000-01-01')
        if len(taiwan_exports) > 0:
            db.insert_indicator_data(
                'taiwan_exports',
                taiwan_exports,
                'FRED',
                'XTEXVA01TWM667S',
                'Taiwan Exports of Goods and Services'
            )
            print(f"   ✓ Added Taiwan Exports: {len(taiwan_exports)} records")
            print(f"   Latest: {taiwan_exports['value'].iloc[-1]:.2f} ({taiwan_exports['date'].iloc[-1].strftime('%Y-%m-%d')})")

            # Calculate YoY%
            taiwan_yoy = taiwan_exports.copy()
            taiwan_yoy['value'] = calculate_yoy_percent(taiwan_yoy['value'])
            taiwan_yoy = taiwan_yoy.dropna()
            db.insert_indicator_data(
                'taiwan_exports_yoy',
                taiwan_yoy,
                'Calculated',
                'XTEXVA01TWM667S_YOY',
                'Taiwan Exports YoY %'
            )
            print(f"   ✓ Added Taiwan Exports YoY%: {len(taiwan_yoy)} records")
    except Exception as e:
        print(f"   ⚠ Taiwan Exports error: {e}")
        print("   Trying alternative series...")
        try:
            # Try total trade
            taiwan_trade = fetcher.fetch_series('XTNTVA01TWM188S', start_date='2000-01-01')
            if len(taiwan_trade) > 0:
                db.insert_indicator_data(
                    'taiwan_trade',
                    taiwan_trade,
                    'FRED',
                    'XTNTVA01TWM188S',
                    'Taiwan Total Trade'
                )
                print(f"   ✓ Added Taiwan Trade (proxy): {len(taiwan_trade)} records")
        except Exception as e2:
            print(f"   ✗ Alternative failed: {e2}")

    # 2. Commodity Currencies (AUD/USD, CAD/USD)
    print("\n2. Fetching Commodity Currencies...")

    # AUD/USD
    try:
        audusd = fetcher.fetch_series('DEXUSAL', start_date='2000-01-01')
        if len(audusd) > 0:
            db.insert_indicator_data(
                'audusd',
                audusd,
                'FRED',
                'DEXUSAL',
                'Australian Dollar / US Dollar Exchange Rate'
            )
            print(f"   ✓ Added AUD/USD: {len(audusd)} records")

            # YoY%
            audusd_yoy = audusd.copy()
            audusd_yoy['value'] = calculate_yoy_percent(audusd_yoy['value'])
            audusd_yoy = audusd_yoy.dropna()
            db.insert_indicator_data(
                'audusd_yoy',
                audusd_yoy,
                'Calculated',
                'DEXUSAL_YOY',
                'AUD/USD YoY %'
            )
            print(f"   ✓ Added AUD/USD YoY%: {len(audusd_yoy)} records")
    except Exception as e:
        print(f"   ⚠ AUD/USD error: {e}")

    # CAD/USD
    try:
        cadusd = fetcher.fetch_series('DEXCAUS', start_date='2000-01-01')
        if len(cadusd) > 0:
            db.insert_indicator_data(
                'cadusd',
                cadusd,
                'FRED',
                'DEXCAUS',
                'Canadian Dollar / US Dollar Exchange Rate'
            )
            print(f"   ✓ Added CAD/USD: {len(cadusd)} records")

            # YoY%
            cadusd_yoy = cadusd.copy()
            cadusd_yoy['value'] = calculate_yoy_percent(cadusd_yoy['value'])
            cadusd_yoy = cadusd_yoy.dropna()
            db.insert_indicator_data(
                'cadusd_yoy',
                cadusd_yoy,
                'Calculated',
                'DEXCAUS_YOY',
                'CAD/USD YoY %'
            )
            print(f"   ✓ Added CAD/USD YoY%: {len(cadusd_yoy)} records")
    except Exception as e:
        print(f"   ⚠ CAD/USD error: {e}")

    # 3. Materials Sector ETF (XLB)
    print("\n3. Fetching Materials Sector...")
    try:
        xlb = yf.Ticker("XLB")
        xlb_hist = xlb.history(start="2000-01-01", end=pd.Timestamp.now())

        if len(xlb_hist) > 0:
            xlb_data = pd.DataFrame({
                'date': xlb_hist.index,
                'value': xlb_hist['Close'].values
            })
            xlb_data['date'] = pd.to_datetime(xlb_data['date']).dt.tz_localize(None).dt.normalize()

            db.insert_indicator_data(
                'materials_sector_xlb',
                xlb_data,
                'Yahoo Finance',
                'XLB',
                'Materials Select Sector SPDR Fund'
            )
            print(f"   ✓ Added Materials Sector (XLB): {len(xlb_data)} records")

            # YoY%
            xlb_yoy = xlb_data.copy()
            xlb_yoy['value'] = calculate_yoy_percent(xlb_yoy['value'])
            xlb_yoy = xlb_yoy.dropna()
            db.insert_indicator_data(
                'materials_sector_xlb_yoy',
                xlb_yoy,
                'Calculated',
                'XLB_YOY',
                'Materials Sector YoY %'
            )
            print(f"   ✓ Added Materials Sector YoY%: {len(xlb_yoy)} records")
    except Exception as e:
        print(f"   ✗ Materials Sector error: {e}")

    # 4. Create YoY% versions of key existing indicators
    print("\n4. Creating YoY% versions of key indicators...")

    key_indicators = [
        ('copper_gold_ratio_proper', 'copper_gold_ratio_yoy', 'Copper/Gold Ratio YoY %'),
        ('industrial_production_manufacturing', 'industrial_production_yoy', 'Industrial Production YoY %'),
        ('copper_price_usd_lb', 'copper_price_yoy', 'Copper Price YoY %'),
    ]

    for source_key, target_key, description in key_indicators:
        try:
            data = db.get_indicator_data(source_key)
            if len(data) > 0:
                yoy_data = data.copy()
                # For monthly data, use 12-month change
                yoy_data = yoy_data.sort_values('date')
                yoy_data['value'] = yoy_data['value'].pct_change(periods=12) * 100
                yoy_data = yoy_data.dropna()

                if len(yoy_data) > 0:
                    db.insert_indicator_data(
                        target_key,
                        yoy_data,
                        'Calculated',
                        f'{source_key}_YOY',
                        description
                    )
                    print(f"   ✓ Added {target_key}: {len(yoy_data)} records")
        except Exception as e:
            print(f"   ⚠ {target_key} error: {e}")

    # 5. Financial Conditions Index proxy
    print("\n5. Creating Financial Conditions Index proxy...")
    try:
        # Combine: Credit spreads, VIX, Dollar Index, Treasury yields
        # Using High Yield Spreads as main component
        spreads = db.get_indicator_data('high_yield_spread')
        vix = db.get_indicator_data('vix')
        dxy = db.get_indicator_data('dollar_index')

        # Simple composite: Normalize and combine
        # Higher = tighter conditions, Lower = easier conditions
        if len(spreads) > 0 and len(vix) > 0 and len(dxy) > 0:
            # Merge all three
            fc = spreads[['date', 'value']].copy()
            fc = fc.rename(columns={'value': 'spreads'})

            vix_merge = vix[['date', 'value']].rename(columns={'value': 'vix'})
            dxy_merge = dxy[['date', 'value']].rename(columns={'value': 'dxy'})

            fc = pd.merge(fc, vix_merge, on='date', how='inner')
            fc = pd.merge(fc, dxy_merge, on='date', how='inner')

            # Normalize each component (z-score)
            for col in ['spreads', 'vix', 'dxy']:
                fc[f'{col}_norm'] = (fc[col] - fc[col].mean()) / fc[col].std()

            # Composite: Higher = tighter, invert so higher = easier
            fc['value'] = -(fc['spreads_norm'] + fc['vix_norm'] * 0.5 + fc['dxy_norm'] * 0.3)
            fc_final = fc[['date', 'value']]

            db.insert_indicator_data(
                'financial_conditions_proxy',
                fc_final,
                'Calculated',
                'FC_PROXY',
                'Financial Conditions Index (proxy: inverted spreads + VIX + DXY)'
            )
            print(f"   ✓ Added Financial Conditions proxy: {len(fc_final)} records")
            print("   Note: Higher values = easier financial conditions")
    except Exception as e:
        print(f"   ⚠ Financial Conditions proxy error: {e}")

    # 6. Verify critical indicators exist
    print("\n6. Verifying critical indicators...")
    critical = ['copper_gold_ratio_proper', 'ism_manufacturing_new_orders',
                'russell_2000', 'bitcoin_price', 'm2sl', 'sofr_dff_spread']

    for indicator in critical:
        try:
            data = db.get_indicator_data(indicator)
            print(f"   ✓ {indicator}: {len(data)} records")
        except:
            print(f"   ⚠ {indicator}: NOT FOUND")

    db.close()

    print("\n" + "=" * 70)
    print("✅ REAL VISION DATA SERIES ADDED")
    print("=" * 70)
    print("\nNew series available:")
    print("  • Taiwan Exports (leads ISM for AI cycle)")
    print("  • AUD/USD & CAD/USD (commodity currencies)")
    print("  • Materials Sector XLB")
    print("  • YoY% versions of Cu/Au, Copper, Industrial Production")
    print("  • Financial Conditions Index proxy")
    print("\nReady to create Real Vision-style charts!")

if __name__ == "__main__":
    main()
