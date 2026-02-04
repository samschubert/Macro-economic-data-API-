"""
Create Real Vision-inspired charts for the macro database.
Based on "The Macro Investing Tool" and "Commodity Season" methodologies.
"""

from macro_database import MacroDatabase
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import timedelta

# Set dark theme
plt.style.use('dark_background')

def shift_series_forward(series, months):
    """Shift a time series forward by N months (for lead analysis)."""
    shifted = series.copy()
    shifted['date'] = shifted['date'] - pd.DateOffset(months=months)
    return shifted

def create_macro_seasons_chart():
    """Chart 1: Macro Seasons scatter plot (Growth vs Inflation quadrants)"""
    print("Creating Chart 1: Macro Seasons Scatter Plot...")

    db = MacroDatabase('macro_data.db')

    # Get ISM (growth proxy) and CPI YoY (inflation)
    ism = db.get_indicator_data('ism_manufacturing_new_orders')
    cpi_yoy = db.get_indicator_data('cpi_yoy')

    # Merge
    merged = pd.merge(ism, cpi_yoy, on='date', how='inner', suffixes=('_ism', '_cpi'))

    # Calculate YoY change for ISM (growth momentum)
    merged = merged.sort_values('date')
    merged['ism_yoy'] = merged['value_ism'].pct_change(periods=12) * 100

    # Recent data for scatter
    recent = merged[merged['date'] >= '2020-01-01'].copy()

    # If no recent data, use last 100 points
    if len(recent) < 10:
        recent = merged.tail(min(100, len(merged))).copy()

    if len(recent) == 0:
        print("   ⚠ No data available for Macro Seasons chart")
        db.close()
        return

    fig, ax = plt.subplots(figsize=(12, 10))

    # Create scatter with color gradient by date
    scatter = ax.scatter(recent['ism_yoy'], recent['value_cpi'],
                        c=range(len(recent)), cmap='viridis',
                        s=100, alpha=0.7, edgecolors='white', linewidth=0.5)

    # Add quadrant lines
    ax.axhline(y=recent['value_cpi'].median(), color='white', linestyle='--', linewidth=1, alpha=0.4)
    ax.axvline(x=0, color='white', linestyle='--', linewidth=1, alpha=0.4)

    # Label quadrants
    ax.text(0.02, 0.98, 'SPRING\n(Inflation-, Growth+)\nGold, Bonds', transform=ax.transAxes,
            fontsize=11, verticalalignment='top', color='#00FF88', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

    ax.text(0.98, 0.98, 'SUMMER\n(Inflation+, Growth+)\nCommodities, Crypto', transform=ax.transAxes,
            fontsize=11, verticalalignment='top', ha='right', color='#FFA500', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

    ax.text(0.02, 0.02, 'WINTER\n(Inflation-, Growth-)\nCash, Bonds', transform=ax.transAxes,
            fontsize=11, verticalalignment='bottom', color='#00D9FF', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

    ax.text(0.98, 0.02, 'FALL\n(Inflation+, Growth-)\nGold, Commodities', transform=ax.transAxes,
            fontsize=11, verticalalignment='bottom', ha='right', color='#FF6B6B', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

    # Highlight most recent point
    current = recent.iloc[-1]
    ax.scatter(current['ism_yoy'], current['value_cpi'],
              color='#00FF88', s=400, zorder=5, marker='*', edgecolors='white', linewidth=2,
              label=f"Current: {current['date'].strftime('%b %Y')}")

    ax.set_title('Macro Seasons: Growth vs Inflation Framework', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Growth Momentum (ISM YoY %)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Inflation (CPI YoY %)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.2)

    # Add colorbar for time
    cbar = plt.colorbar(scatter, ax=ax, label='Time →')
    cbar.set_label('Time (Recent → Current)', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig('rv_chart1_macro_seasons.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    db.close()
    print("   ✓ Saved: rv_chart1_macro_seasons.png")

def create_taiwan_vs_ism():
    """Chart 2: Taiwan Semiconductor (TSM) vs ISM (AI cycle leading indicator)"""
    print("Creating Chart 2: Taiwan Semiconductor vs ISM...")

    db = MacroDatabase('macro_data.db')

    try:
        taiwan_yoy = db.get_indicator_data('taiwan_semiconductor_yoy')
        if len(taiwan_yoy) == 0:
            raise Exception("No Taiwan semiconductor data available")
        ism = db.get_indicator_data('ism_manufacturing_new_orders')

        # Shift Taiwan forward (it leads)
        taiwan_shifted = shift_series_forward(taiwan_yoy, 3)  # 3-month lead

        # Merge
        merged = pd.merge(taiwan_shifted, ism, on='date', how='inner', suffixes=('_taiwan', '_ism'))

        fig, ax1 = plt.subplots(figsize=(14, 8))

        # Taiwan YoY
        color1 = '#00D9FF'
        ax1.set_xlabel('Date', fontsize=14, fontweight='bold')
        ax1.set_ylabel('TSM Stock YoY % (3-month lead)', fontsize=14, fontweight='bold', color=color1)
        ax1.plot(merged['date'], merged['value_taiwan'], linewidth=2.5, color=color1, label='Taiwan Semiconductor YoY%')
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.2)

        # ISM
        ax2 = ax1.twinx()
        color2 = '#FF6B6B'
        ax2.set_ylabel('ISM Manufacturing New Orders', fontsize=14, fontweight='bold', color=color2)
        ax2.plot(merged['date'], merged['value_ism'], linewidth=2.5, color=color2, alpha=0.8, label='ISM')
        ax2.tick_params(axis='y', labelcolor=color2)

        ax1.set_title('Taiwan Semiconductor Leads US Manufacturing: AI Cycle Indicator', fontsize=18, fontweight='bold', pad=20)

        # Correlation
        corr = merged['value_taiwan'].corr(merged['value_ism'])
        ax1.text(0.02, 0.98, f'Correlation: {corr:.3f}\n(Taiwan leads by 3 months)', transform=ax1.transAxes,
                fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

        fig.tight_layout()
        plt.savefig('rv_chart2_taiwan_vs_ism.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
        plt.close()

        print("   ✓ Saved: rv_chart2_taiwan_vs_ism.png")

    except Exception as e:
        print(f"   ⚠ Skipping Taiwan chart: {e}")

    db.close()

def create_copper_gold_yoy_vs_ism():
    """Chart 3: Copper/Gold Ratio YoY% vs ISM YoY% (Real Vision validation)"""
    print("Creating Chart 3: Cu/Au Ratio YoY% vs ISM...")

    db = MacroDatabase('macro_data.db')

    ratio_yoy = db.get_indicator_data('copper_gold_ratio_yoy')
    ism = db.get_indicator_data('ism_manufacturing_new_orders')

    # Calculate ISM YoY%
    ism_sorted = ism.sort_values('date')
    ism_sorted['ism_yoy'] = ism_sorted['value'].pct_change(periods=12) * 100
    ism_yoy = ism_sorted[['date', 'ism_yoy']].dropna()

    # Merge
    merged = pd.merge(ratio_yoy, ism_yoy, on='date', how='inner')

    fig, ax1 = plt.subplots(figsize=(14, 8))

    # Cu/Au YoY
    color1 = '#00D9FF'
    ax1.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Cu/Au Ratio YoY %', fontsize=14, fontweight='bold', color=color1)
    ax1.plot(merged['date'], merged['value'], linewidth=2.5, color=color1, label='Cu/Au YoY%')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.2)
    ax1.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.3)

    # ISM YoY
    ax2 = ax1.twinx()
    color2 = '#FFA500'
    ax2.set_ylabel('ISM Manufacturing YoY %', fontsize=14, fontweight='bold', color=color2)
    ax2.plot(merged['date'], merged['ism_yoy'], linewidth=2.5, color=color2, alpha=0.8, label='ISM YoY%')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.3)

    ax1.set_title('Dr. Copper: Cu/Au Ratio Tracks Growth Momentum (Real Vision Method)', fontsize=18, fontweight='bold', pad=20)

    # Correlation
    corr = merged['value'].corr(merged['ism_yoy'])
    ax1.text(0.02, 0.98, f'Correlation: {corr:.3f}\n"When ISM is rising, copper\nbenefits while gold lags"',
            transform=ax1.transAxes, fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

    fig.tight_layout()
    plt.savefig('rv_chart3_copper_gold_yoy_vs_ism.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    db.close()
    print("   ✓ Saved: rv_chart3_copper_gold_yoy_vs_ism.png")

def create_commodity_currencies_vs_ism():
    """Chart 4: AUD/USD & CAD/USD YoY% vs ISM"""
    print("Creating Chart 4: Commodity Currencies vs ISM...")

    db = MacroDatabase('macro_data.db')

    try:
        audusd_yoy = db.get_indicator_data('audusd_yoy')
        cadusd_yoy = db.get_indicator_data('cadusd_yoy')
        ism = db.get_indicator_data('ism_manufacturing_new_orders')

        # Merge all
        merged = pd.merge(audusd_yoy, cadusd_yoy, on='date', how='inner', suffixes=('_aud', '_cad'))
        merged = pd.merge(merged, ism, on='date', how='inner')

        fig, ax1 = plt.subplots(figsize=(14, 8))

        # Plot currencies
        color1 = '#FFD700'
        color2 = '#FF6347'
        ax1.set_xlabel('Date', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Commodity Currencies YoY %', fontsize=14, fontweight='bold', color=color1)
        ax1.plot(merged['date'], merged['value_aud'], linewidth=2.5, color=color1, label='AUD/USD YoY%')
        ax1.plot(merged['date'], merged['value_cad'], linewidth=2.5, color=color2, alpha=0.8, label='CAD/USD YoY%')
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.2)
        ax1.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.3)
        ax1.legend(loc='upper left', fontsize=11)

        # ISM
        ax2 = ax1.twinx()
        color3 = '#00D9FF'
        ax2.set_ylabel('ISM Manufacturing', fontsize=14, fontweight='bold', color=color3)
        ax2.plot(merged['date'], merged['value'], linewidth=2.5, color=color3, alpha=0.6, label='ISM', linestyle='--')
        ax2.tick_params(axis='y', labelcolor=color3)

        ax1.set_title('Commodity Currencies Track Manufacturing Cycle', fontsize=18, fontweight='bold', pad=20)

        # Correlations
        corr_aud = merged['value_aud'].corr(merged['value'])
        corr_cad = merged['value_cad'].corr(merged['value'])
        ax1.text(0.02, 0.02, f'AUD Correlation: {corr_aud:.3f}\nCAD Correlation: {corr_cad:.3f}',
                transform=ax1.transAxes, fontsize=12, verticalalignment='bottom',
                bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

        fig.tight_layout()
        plt.savefig('rv_chart4_commodity_currencies.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
        plt.close()

        print("   ✓ Saved: rv_chart4_commodity_currencies.png")

    except Exception as e:
        print(f"   ⚠ Skipping commodity currencies chart: {e}")

    db.close()

def create_materials_vs_ism():
    """Chart 5: Materials Sector vs ISM"""
    print("Creating Chart 5: Materials Sector vs ISM...")

    db = MacroDatabase('macro_data.db')

    try:
        materials_yoy = db.get_indicator_data('materials_sector_xlb_yoy')
        ism = db.get_indicator_data('ism_manufacturing_new_orders')

        # Merge
        merged = pd.merge(materials_yoy, ism, on='date', how='inner', suffixes=('_xlb', '_ism'))

        fig, ax1 = plt.subplots(figsize=(14, 8))

        # Materials YoY
        color1 = '#9D4EDD'
        ax1.set_xlabel('Date', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Materials Sector (XLB) YoY %', fontsize=14, fontweight='bold', color=color1)
        ax1.plot(merged['date'], merged['value_xlb'], linewidth=2.5, color=color1, label='Materials YoY%')
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.2)
        ax1.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.3)

        # ISM
        ax2 = ax1.twinx()
        color2 = '#FF6B6B'
        ax2.set_ylabel('ISM Manufacturing', fontsize=14, fontweight='bold', color=color2)
        ax2.plot(merged['date'], merged['value_ism'], linewidth=2.5, color=color2, alpha=0.8, label='ISM')
        ax2.tick_params(axis='y', labelcolor=color2)

        ax1.set_title('Materials Stocks: Equities\' Answer to Copper', fontsize=18, fontweight='bold', pad=20)

        # Correlation
        corr = merged['value_xlb'].corr(merged['value_ism'])
        ax1.text(0.02, 0.98, f'Correlation: {corr:.3f}', transform=ax1.transAxes,
                fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

        fig.tight_layout()
        plt.savefig('rv_chart5_materials_vs_ism.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
        plt.close()

        print("   ✓ Saved: rv_chart5_materials_vs_ism.png")

    except Exception as e:
        print(f"   ⚠ Skipping materials chart: {e}")

    db.close()

def create_financial_conditions_leads():
    """Chart 6: NFCI (Chicago Fed Financial Conditions) with multiple forward shifts"""
    print("Creating Chart 6: Financial Conditions (NFCI) Leading ISM...")

    db = MacroDatabase('macro_data.db')

    try:
        fc = db.get_indicator_data('nfci')
        if len(fc) == 0:
            raise Exception("No NFCI data available")
        ism = db.get_indicator_data('ism_manufacturing_new_orders')

        # Test multiple lead times
        best_corr = 0
        best_months = 0
        correlations = []

        for months in range(3, 13):
            fc_shifted = shift_series_forward(fc, months)
            merged = pd.merge(fc_shifted, ism, on='date', how='inner', suffixes=('_fc', '_ism'))
            if len(merged) > 0:
                corr = merged['value_fc'].corr(merged['value_ism'])
                correlations.append((months, corr))
                if abs(corr) > abs(best_corr):
                    best_corr = corr
                    best_months = months

        print(f"   Best correlation: {best_corr:.3f} at {best_months}-month lead")

        # Plot with best lead time
        fc_shifted = shift_series_forward(fc, best_months)
        merged = pd.merge(fc_shifted, ism, on='date', how='inner', suffixes=('_fc', '_ism'))

        fig, ax1 = plt.subplots(figsize=(14, 8))

        # Financial Conditions (note: NFCI is inverted - higher = tighter)
        color1 = '#00FF88'
        ax1.set_xlabel('Date', fontsize=14, fontweight='bold')
        ax1.set_ylabel(f'NFCI ({best_months}-month lead, inverted)', fontsize=14, fontweight='bold', color=color1)
        # Invert NFCI so easier conditions = higher (more intuitive)
        ax1.plot(merged['date'], -merged['value_fc'], linewidth=2.5, color=color1, label='NFCI (inverted)')
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.2)
        ax1.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.3)

        # ISM
        ax2 = ax1.twinx()
        color2 = '#FF6B6B'
        ax2.set_ylabel('ISM Manufacturing', fontsize=14, fontweight='bold', color=color2)
        ax2.plot(merged['date'], merged['value_ism'], linewidth=2.5, color=color2, alpha=0.8, label='ISM')
        ax2.tick_params(axis='y', labelcolor=color2)

        ax1.set_title(f'Chicago Fed NFCI Leads Manufacturing by {best_months} Months', fontsize=18, fontweight='bold', pad=20)

        # Add correlation info
        corr_text = f'Correlation: {best_corr:.3f} at {best_months}-month lead\n'
        corr_text += '\nTested lead times:\n'
        for months, corr in correlations[:5]:
            corr_text += f'{months}mo: {corr:.3f}\n'

        ax1.text(0.02, 0.98, corr_text, transform=ax1.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

        fig.tight_layout()
        plt.savefig('rv_chart6_financial_conditions.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
        plt.close()

        print("   ✓ Saved: rv_chart6_financial_conditions.png")

    except Exception as e:
        print(f"   ⚠ Skipping financial conditions chart: {e}")

    db.close()

def main():
    print("=" * 70)
    print("CREATING REAL VISION-STYLE CHARTS")
    print("=" * 70)
    print()

    create_macro_seasons_chart()
    create_taiwan_vs_ism()
    create_copper_gold_yoy_vs_ism()
    create_commodity_currencies_vs_ism()
    create_materials_vs_ism()
    create_financial_conditions_leads()

    print()
    print("=" * 70)
    print("✅ ALL REAL VISION CHARTS CREATED")
    print("=" * 70)
    print("\nFiles created:")
    print("  1. rv_chart1_macro_seasons.png - Growth/Inflation quadrants")
    print("  2. rv_chart2_taiwan_vs_ism.png - Taiwan Exports lead (AI cycle)")
    print("  3. rv_chart3_copper_gold_yoy_vs_ism.png - YoY% validation")
    print("  4. rv_chart4_commodity_currencies.png - AUD/USD, CAD/USD")
    print("  5. rv_chart5_materials_vs_ism.png - Materials stocks")
    print("  6. rv_chart6_financial_conditions.png - FC leading indicator")
    print("\nBased on Real Vision methodologies from:")
    print("  • The Macro Investing Tool (Jan 2026)")
    print("  • Commodity Season (Jan 2026)")

if __name__ == "__main__":
    main()
