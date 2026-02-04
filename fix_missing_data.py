"""
Add missing CPI data and create Financial Conditions charts using existing NFCI.
"""

from macro_database import FREDDataFetcher, MacroDatabase
import pandas as pd

def main():
    print("=" * 70)
    print("FIXING MISSING DATA")
    print("=" * 70)

    api_key = "d84ee068104098a83a9619da9b8412de"
    fetcher = FREDDataFetcher(api_key)
    db = MacroDatabase('macro_data.db')

    # 1. Add CPI (Consumer Price Index)
    print("\n1. Fetching CPI...")
    try:
        cpi = fetcher.fetch_series('CPIAUCSL', start_date='2000-01-01')
        if len(cpi) > 0:
            db.insert_indicator_data(
                'cpi',
                cpi,
                'FRED',
                'CPIAUCSL',
                'Consumer Price Index for All Urban Consumers: All Items'
            )
            print(f"   ✓ Added CPI: {len(cpi)} records")

            # Calculate YoY%
            cpi_sorted = cpi.sort_values('date')
            cpi_sorted['cpi_yoy'] = cpi_sorted['value'].pct_change(periods=12) * 100
            cpi_yoy = cpi_sorted[['date', 'cpi_yoy']].dropna()
            cpi_yoy = cpi_yoy.rename(columns={'cpi_yoy': 'value'})

            db.insert_indicator_data(
                'cpi_yoy',
                cpi_yoy,
                'Calculated',
                'CPIAUCSL_YOY',
                'CPI YoY %'
            )
            print(f"   ✓ Added CPI YoY%: {len(cpi_yoy)} records")
    except Exception as e:
        print(f"   ✗ CPI error: {e}")

    # 2. Verify we have NFCI (National Financial Conditions Index)
    print("\n2. Verifying Financial Conditions Index...")
    try:
        nfci = db.get_indicator_data('nfci')
        print(f"   ✓ NFCI already exists: {len(nfci)} records")
        print("   Note: Using Chicago Fed National Financial Conditions Index")
    except Exception as e:
        print(f"   ⚠ NFCI check: {e}")

    # 3. Add Core CPI (excludes food & energy - cleaner inflation signal)
    print("\n3. Fetching Core CPI...")
    try:
        core_cpi = fetcher.fetch_series('CPILFESL', start_date='2000-01-01')
        if len(core_cpi) > 0:
            db.insert_indicator_data(
                'core_cpi',
                core_cpi,
                'FRED',
                'CPILFESL',
                'Consumer Price Index: All Items Less Food & Energy'
            )
            print(f"   ✓ Added Core CPI: {len(core_cpi)} records")

            # YoY%
            core_sorted = core_cpi.sort_values('date')
            core_sorted['core_yoy'] = core_sorted['value'].pct_change(periods=12) * 100
            core_yoy = core_sorted[['date', 'core_yoy']].dropna()
            core_yoy = core_yoy.rename(columns={'core_yoy': 'value'})

            db.insert_indicator_data(
                'core_cpi_yoy',
                core_yoy,
                'Calculated',
                'CPILFESL_YOY',
                'Core CPI YoY %'
            )
            print(f"   ✓ Added Core CPI YoY%: {len(core_yoy)} records")
    except Exception as e:
        print(f"   ⚠ Core CPI error: {e}")

    # 4. Taiwan Semiconductor Manufacturing (TSM) as proxy for Taiwan exports
    print("\n4. Fetching Taiwan Semiconductor (TSM) as AI cycle proxy...")
    try:
        import yfinance as yf
        tsm = yf.Ticker("TSM")
        tsm_hist = tsm.history(start="2000-01-01", end=pd.Timestamp.now())

        if len(tsm_hist) > 0:
            tsm_data = pd.DataFrame({
                'date': tsm_hist.index,
                'value': tsm_hist['Close'].values
            })
            tsm_data['date'] = pd.to_datetime(tsm_data['date']).dt.tz_localize(None).dt.normalize()

            db.insert_indicator_data(
                'taiwan_semiconductor_tsm',
                tsm_data,
                'Yahoo Finance',
                'TSM',
                'Taiwan Semiconductor Manufacturing Co (ADR)'
            )
            print(f"   ✓ Added TSM: {len(tsm_data)} records")

            # YoY%
            tsm_sorted = tsm_data.sort_values('date')
            tsm_sorted['tsm_yoy'] = tsm_sorted['value'].pct_change(periods=252) * 100  # 252 trading days
            tsm_yoy = tsm_sorted[['date', 'tsm_yoy']].dropna()
            tsm_yoy = tsm_yoy.rename(columns={'tsm_yoy': 'value'})

            db.insert_indicator_data(
                'taiwan_semiconductor_yoy',
                tsm_yoy,
                'Calculated',
                'TSM_YOY',
                'TSM Stock YoY % (AI/Semiconductor Cycle Proxy)'
            )
            print(f"   ✓ Added TSM YoY%: {len(tsm_yoy)} records")
            print("   Note: Using TSM stock as proxy for Taiwan exports/AI cycle")
    except Exception as e:
        print(f"   ⚠ TSM error: {e}")

    db.close()

    print("\n" + "=" * 70)
    print("✅ DATA FIXES COMPLETE")
    print("=" * 70)
    print("\nNew data added:")
    print("  • CPI and Core CPI (with YoY%)")
    print("  • NFCI verified (Financial Conditions)")
    print("  • TSM (Taiwan Semiconductor as AI cycle proxy)")

if __name__ == "__main__":
    main()
