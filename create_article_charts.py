"""
Create publication-ready charts for the copper/gold ratio article.
Dark theme, clean design, ready for publication.
"""

from macro_database import MacroDatabase
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

# Set dark theme
plt.style.use('dark_background')

def create_copper_gold_longterm():
    """Chart 1: Copper/Gold Ratio Long-term with reference lines"""
    print("Creating Chart 1: Copper/Gold Ratio Long-term...")

    db = MacroDatabase('macro_data.db')
    ratio = db.get_indicator_data('copper_gold_ratio_proper')

    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot ratio
    ax.plot(ratio['date'], ratio['value'], linewidth=2.5, color='#00D9FF', label='Cu/Au Ratio')

    # Reference lines
    crisis_2008 = 0.00165  # Approximate 2008 crisis level
    covid_2020 = 0.00145   # March 2020 COVID low
    current = ratio['value'].iloc[-1]

    ax.axhline(y=crisis_2008, color='#FF6B6B', linestyle='--', linewidth=1.5,
               label=f'2008 Crisis (~{crisis_2008:.5f})', alpha=0.7)
    ax.axhline(y=covid_2020, color='#FFA500', linestyle='--', linewidth=1.5,
               label=f'March 2020 COVID (~{covid_2020:.5f})', alpha=0.7)
    ax.axhline(y=current, color='#00FF88', linestyle='--', linewidth=1.5,
               label=f'Current ({current:.6f})', alpha=0.7)

    # Mark key bottoms
    # Jan 2016 bottom
    jan_2016 = ratio[ratio['date'].dt.to_period('M') == '2016-01']
    if len(jan_2016) > 0:
        ax.scatter(jan_2016['date'].iloc[0], jan_2016['value'].iloc[0],
                  color='#FF4444', s=150, zorder=5, marker='v', label='Jan 2016 Bottom')

    # July 2020 bottom
    july_2020 = ratio[(ratio['date'].dt.year == 2020) & (ratio['date'].dt.month == 7)]
    if len(july_2020) > 0:
        ax.scatter(july_2020['date'].iloc[0], july_2020['value'].iloc[0],
                  color='#FF4444', s=150, zorder=5, marker='v', label='July 2020 Bottom')

    # Oct 2025 bottom (or most recent low)
    recent_data = ratio[ratio['date'] >= '2025-01-01']
    if len(recent_data) > 0:
        min_idx = recent_data['value'].idxmin()
        ax.scatter(recent_data.loc[min_idx, 'date'], recent_data.loc[min_idx, 'value'],
                  color='#00FF88', s=200, zorder=5, marker='v', label='Oct 2025 Bottom')

    ax.set_title('Copper/Gold Ratio: 50-Year Lows Signal Risk-On Ahead', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('Cu/Au Ratio ($/lb ÷ $/oz)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(True, alpha=0.2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.tight_layout()
    plt.savefig('article_chart1_ratio_longterm.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    db.close()
    print("   ✓ Saved: article_chart1_ratio_longterm.png")

def create_ratio_vs_ism():
    """Chart 2: Copper/Gold Ratio vs ISM Manufacturing"""
    print("Creating Chart 2: Cu/Au Ratio vs ISM Manufacturing...")

    db = MacroDatabase('macro_data.db')
    ratio = db.get_indicator_data('copper_gold_ratio_proper')

    # Try ISM New Orders, fallback to Industrial Production
    try:
        ism = db.get_indicator_data('ism_manufacturing_new_orders')
        ism_label = 'ISM Manufacturing: New Orders Index'
    except:
        ism = db.get_indicator_data('industrial_production_manufacturing')
        ism_label = 'Industrial Production: Manufacturing'

    # Merge on date
    merged = pd.merge(ratio, ism, on='date', how='inner', suffixes=('_ratio', '_ism'))

    fig, ax1 = plt.subplots(figsize=(14, 8))

    # Plot ratio
    color1 = '#00D9FF'
    ax1.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Cu/Au Ratio', fontsize=14, fontweight='bold', color=color1)
    ax1.plot(merged['date'], merged['value_ratio'], linewidth=2.5, color=color1, label='Cu/Au Ratio')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.2)

    # Plot ISM on second axis
    ax2 = ax1.twinx()
    color2 = '#FF6B6B'
    ax2.set_ylabel(ism_label, fontsize=14, fontweight='bold', color=color2)
    ax2.plot(merged['date'], merged['value_ism'], linewidth=2.5, color=color2, alpha=0.8, label=ism_label)
    ax2.tick_params(axis='y', labelcolor=color2)

    ax1.set_title('Copper/Gold Ratio Leads Manufacturing Recovery', fontsize=18, fontweight='bold', pad=20)

    # Add correlation annotation
    corr = merged['value_ratio'].corr(merged['value_ism'])
    ax1.text(0.02, 0.98, f'Correlation: {corr:.3f}', transform=ax1.transAxes,
             fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

    fig.tight_layout()
    plt.savefig('article_chart2_ratio_vs_ism.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    db.close()
    print("   ✓ Saved: article_chart2_ratio_vs_ism.png")

def create_ratio_vs_bitcoin():
    """Chart 3: Copper/Gold Ratio vs Bitcoin with cycle peaks"""
    print("Creating Chart 3: Cu/Au Ratio vs Bitcoin (cycle peaks)...")

    db = MacroDatabase('macro_data.db')
    ratio = db.get_indicator_data('copper_gold_ratio_proper')
    btc = db.get_indicator_data('bitcoin_price')

    # Normalize timezones
    ratio['date'] = pd.to_datetime(ratio['date']).dt.tz_localize(None)
    btc['date'] = pd.to_datetime(btc['date']).dt.tz_localize(None)

    # Merge
    merged = pd.merge(ratio, btc, on='date', how='inner', suffixes=('_ratio', '_btc'))

    fig, ax1 = plt.subplots(figsize=(14, 8))

    # Plot ratio
    color1 = '#00D9FF'
    ax1.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Cu/Au Ratio', fontsize=14, fontweight='bold', color=color1)
    ax1.plot(merged['date'], merged['value_ratio'], linewidth=2.5, color=color1, label='Cu/Au Ratio')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.2)

    # Plot Bitcoin on log scale
    ax2 = ax1.twinx()
    color2 = '#FFA500'
    ax2.set_ylabel('Bitcoin Price (USD, log scale)', fontsize=14, fontweight='bold', color=color2)
    ax2.semilogy(merged['date'], merged['value_btc'], linewidth=2.5, color=color2, alpha=0.8, label='Bitcoin')
    ax2.tick_params(axis='y', labelcolor=color2)

    # Mark cycle peaks
    cycle_peaks = [
        ('2013-11-30', 'Nov 2013\nBTC Peak'),
        ('2017-12-17', 'Dec 2017\nBTC Peak'),
        ('2021-11-10', 'Nov 2021\nBTC Peak'),
    ]

    for peak_date, label in cycle_peaks:
        peak_date = pd.to_datetime(peak_date)
        if peak_date in merged['date'].values:
            ax1.axvline(x=peak_date, color='#FF4444', linestyle='--', linewidth=2, alpha=0.6)
            ax1.text(peak_date, ax1.get_ylim()[1] * 0.95, label,
                    ha='right', fontsize=10, color='#FF4444', fontweight='bold')

    ax1.set_title('Cu/Au Peaks Precede Bitcoin Cycle Tops by 12-60 Days', fontsize=18, fontweight='bold', pad=20)

    fig.tight_layout()
    plt.savefig('article_chart3_ratio_vs_bitcoin.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    db.close()
    print("   ✓ Saved: article_chart3_ratio_vs_bitcoin.png")

def create_ratio_vs_russell():
    """Chart 4: Copper/Gold Ratio vs Russell 2000"""
    print("Creating Chart 4: Cu/Au Ratio vs Russell 2000...")

    db = MacroDatabase('macro_data.db')
    ratio = db.get_indicator_data('copper_gold_ratio_proper')
    rut = db.get_indicator_data('russell_2000')

    # Merge
    merged = pd.merge(ratio, rut, on='date', how='inner', suffixes=('_ratio', '_rut'))

    fig, ax1 = plt.subplots(figsize=(14, 8))

    # Plot ratio
    color1 = '#00D9FF'
    ax1.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Cu/Au Ratio', fontsize=14, fontweight='bold', color=color1)
    ax1.plot(merged['date'], merged['value_ratio'], linewidth=2.5, color=color1, label='Cu/Au Ratio')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.2)

    # Plot Russell 2000
    ax2 = ax1.twinx()
    color2 = '#9D4EDD'
    ax2.set_ylabel('Russell 2000 Index', fontsize=14, fontweight='bold', color=color2)
    ax2.plot(merged['date'], merged['value_rut'], linewidth=2.5, color=color2, alpha=0.8, label='Russell 2000')
    ax2.tick_params(axis='y', labelcolor=color2)

    # Mark Oct 2021 peak
    oct_2021 = pd.to_datetime('2021-10-01')
    ax1.axvline(x=oct_2021, color='#FF4444', linestyle='--', linewidth=2, alpha=0.6)
    ax1.text(oct_2021, ax1.get_ylim()[1] * 0.95, 'Oct 2021\nCu/Au Peak',
            ha='right', fontsize=10, color='#FF4444', fontweight='bold')

    ax1.set_title('Small Caps Track Copper/Gold: Altcoins Are Crypto\'s Small Caps', fontsize=18, fontweight='bold', pad=20)

    # Correlation
    corr = merged['value_ratio'].corr(merged['value_rut'])
    ax1.text(0.02, 0.98, f'Correlation: {corr:.3f}', transform=ax1.transAxes,
             fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

    fig.tight_layout()
    plt.savefig('article_chart4_ratio_vs_russell.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    db.close()
    print("   ✓ Saved: article_chart4_ratio_vs_russell.png")

def create_sofr_spread_chart():
    """Chart 5: SOFR-Fed Funds Spread"""
    print("Creating Chart 5: SOFR-Fed Funds Spread...")

    db = MacroDatabase('macro_data.db')
    spread = db.get_indicator_data('sofr_dff_spread')

    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot spread
    ax.plot(spread['date'], spread['value'], linewidth=2.5, color='#00FF88', label='SOFR-DFF Spread')
    ax.axhline(y=0, color='white', linestyle='-', linewidth=1, alpha=0.3)

    # Highlight Sept 2025 spike
    sept_2025 = spread[(spread['date'] >= '2025-09-01') & (spread['date'] <= '2025-09-30')]
    if len(sept_2025) > 0:
        max_idx = sept_2025['value'].idxmax()
        ax.scatter(sept_2025.loc[max_idx, 'date'], sept_2025.loc[max_idx, 'value'],
                  color='#FF4444', s=200, zorder=5, marker='^', label='Sept 2025 Spike')

    ax.set_title('Liquidity Stress Easing: SOFR-Fed Funds Spread Normalizing', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('Spread (basis points)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig('article_chart5_sofr_spread.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    db.close()
    print("   ✓ Saved: article_chart5_sofr_spread.png")

def create_m2_chart():
    """Chart 6: US M2 Money Supply"""
    print("Creating Chart 6: US M2 Money Supply...")

    db = MacroDatabase('macro_data.db')
    m2 = db.get_indicator_data('m2sl')

    fig, ax = plt.subplots(figsize=(14, 8))

    # Plot M2
    ax.plot(m2['date'], m2['value'], linewidth=2.5, color='#00D9FF', label='M2 Money Supply')

    # Add trend line for recent expansion
    recent = m2[m2['date'] >= '2022-01-01']
    if len(recent) > 5:
        z = np.polyfit(mdates.date2num(recent['date']), recent['value'], 1)
        p = np.poly1d(z)
        ax.plot(recent['date'], p(mdates.date2num(recent['date'])),
               linestyle='--', color='#00FF88', linewidth=2, label='Recent Trend', alpha=0.7)

    ax.set_title('M2 Money Supply: Expansion Resumed After 2022-2023 Contraction', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('M2 (Billions USD)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.tight_layout()
    plt.savefig('article_chart6_m2_money_supply.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    db.close()
    print("   ✓ Saved: article_chart6_m2_money_supply.png")

def main():
    print("=" * 70)
    print("CREATING ARTICLE CHARTS")
    print("=" * 70)
    print()

    create_copper_gold_longterm()
    create_ratio_vs_ism()
    create_ratio_vs_bitcoin()
    create_ratio_vs_russell()
    create_sofr_spread_chart()
    create_m2_chart()

    print()
    print("=" * 70)
    print("✅ ALL ARTICLE CHARTS CREATED")
    print("=" * 70)
    print("\nFiles created:")
    print("  1. article_chart1_ratio_longterm.png")
    print("  2. article_chart2_ratio_vs_ism.png")
    print("  3. article_chart3_ratio_vs_bitcoin.png")
    print("  4. article_chart4_ratio_vs_russell.png")
    print("  5. article_chart5_sofr_spread.png")
    print("  6. article_chart6_m2_money_supply.png")
    print("\nPublication-ready, dark theme, 300 DPI")

if __name__ == "__main__":
    main()
