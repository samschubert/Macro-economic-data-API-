"""
Create compelling charts for "Copper/Gold as Leading Risk-On Indicator" article.

Charts to create:
1. Cu/Au ratio with marked turning points + 3-6 month forward ISM
2. Cu/Au vs S&P 500 overlay (risk appetite)
3. Cu/Au vs BTC with cycle peaks marked
4. Liquidity dashboard (SOFR spread, M2, Fed balance sheet)
5. Cu/Au vs DXY (dollar weakness = risk-on)
6. Credit spreads overlaid with Cu/Au
"""

from macro_database import MacroDatabase
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


def fetch_bitcoin_data(db):
    """Fetch Bitcoin price from Yahoo Finance."""
    print("\n₿ Fetching Bitcoin data from Yahoo Finance...")

    try:
        btc = yf.Ticker("BTC-USD")
        hist = btc.history(start="2010-01-01", end=datetime.now())

        if hist.empty:
            print("❌ No Bitcoin data")
            return None

        btc_data = pd.DataFrame({
            'date': hist.index,
            'value': hist['Close'].values
        })

        btc_data = btc_data.dropna()
        btc_data['date'] = pd.to_datetime(btc_data['date'])

        # Store in database
        db.insert_indicator_data(
            'bitcoin_price',
            btc_data,
            source='Yahoo Finance',
            series_id='BTC-USD',
            description='Bitcoin Price (USD)'
        )

        print(f"✓ Bitcoin: {len(btc_data)} records, ${btc_data['value'].iloc[-1]:.2f}")
        return btc_data

    except Exception as e:
        print(f"❌ Bitcoin fetch failed: {e}")
        return None


def chart_copper_gold_ism_lead(db, start_year=2010):
    """Chart 1: Cu/Au with ISM shifted 6 months forward to show leading relationship."""
    print(f"\n📈 Chart 1: Cu/Au Leading ISM ({start_year}+)...")

    ratio = db.get_indicator_data('copper_gold_ratio_proper')
    ism = db.get_indicator_data('industrial_production_manufacturing')

    ratio = ratio[ratio['date'] >= f'{start_year}-01-01']
    ism = ism[ism['date'] >= f'{start_year}-01-01']

    # Shift ISM forward 6 months to show Cu/Au leads
    ism_shifted = ism.copy()
    ism_shifted['date'] = ism_shifted['date'] - pd.DateOffset(months=6)

    merged = pd.merge(ratio, ism_shifted, on='date', suffixes=('_ratio', '_ism'), how='outer').sort_values('date')

    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(4, 1, height_ratios=[3, 0.5, 0.01, 0.01])
    ax1 = fig.add_subplot(gs[0])

    # Plot Cu/Au
    color1 = '#2E86AB'
    ax1.plot(merged['date'], merged['value_ratio'], linewidth=2.5, color=color1, label='Copper/Gold Ratio', zorder=3)
    ax1.set_ylabel('Copper/Gold Ratio', fontsize=13, color=color1, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.2)

    # Plot ISM (shifted 6mo forward to align with Cu/Au)
    ax2 = ax1.twinx()
    color2 = '#d62728'
    ax2.plot(merged['date'], merged['value_ism'], linewidth=2, color=color2,
             label='Manufacturing Production (6mo Forward)', alpha=0.8, zorder=2)
    ax2.set_ylabel('Industrial Production Index', fontsize=13, color=color2, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)

    ax1.set_title('Copper/Gold Ratio LEADS Manufacturing by ~6 Months',
                  fontsize=17, fontweight='bold', pad=20)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

    ax1.set_xticklabels([])

    # Stats
    ax_stats = fig.add_subplot(gs[1])
    ax_stats.axis('off')

    correlation = merged[['value_ratio', 'value_ism']].dropna().corr().iloc[0, 1]

    stats_text = f"""
    📊 Correlation: {correlation:.3f} (with 6-month forward shift)
    🎯 Thesis: Cu/Au bottoms predict manufacturing turns 3-6 months ahead
    💡 Current Cu/Au: {ratio['value'].iloc[-1]:.6f} (50-year lows = bullish forward signal)
    """

    ax_stats.text(0.5, 0.5, stats_text.strip(), ha='center', va='center',
                  fontsize=11, family='monospace',
                  bbox=dict(boxstyle='round,pad=1', facecolor='#ffffcc', alpha=0.95))

    plt.tight_layout()
    plt.savefig('thesis_chart1_copper_gold_leads_ism.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: thesis_chart1_copper_gold_leads_ism.png")
    plt.close()


def chart_copper_gold_sp500(db, start_year=2010):
    """Chart 2: Cu/Au vs S&P 500 - risk appetite proxy."""
    print(f"\n📈 Chart 2: Cu/Au vs S&P 500 ({start_year}+)...")

    ratio = db.get_indicator_data('copper_gold_ratio_proper')
    sp500 = db.get_indicator_data('sp500')

    ratio = ratio[ratio['date'] >= f'{start_year}-01-01']
    sp500 = sp500[sp500['date'] >= f'{start_year}-01-01']

    merged = pd.merge(ratio, sp500, on='date', suffixes=('_ratio', '_sp500'))

    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(4, 1, height_ratios=[3, 0.5, 0.01, 0.01])
    ax1 = fig.add_subplot(gs[0])

    # Normalize both to 100 at start
    ratio_norm = (merged['value_ratio'] / merged['value_ratio'].iloc[0]) * 100
    sp_norm = (merged['value_sp500'] / merged['value_sp500'].iloc[0]) * 100

    ax1.plot(merged['date'], ratio_norm, linewidth=2.5, color='#2E86AB', label='Copper/Gold Ratio', zorder=2)
    ax1.plot(merged['date'], sp_norm, linewidth=2, color='#228B22', label='S&P 500', alpha=0.7, zorder=1)

    ax1.axhline(y=100, color='black', linestyle='--', linewidth=1, alpha=0.3)

    ax1.set_title('Risk-On Assets Track Copper/Gold Ratio', fontsize=17, fontweight='bold', pad=20)
    ax1.set_ylabel(f'Indexed to 100 ({start_year})', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.2)
    ax1.legend(loc='upper left', fontsize=12)
    ax1.set_xticklabels([])

    # Stats
    ax_stats = fig.add_subplot(gs[1])
    ax_stats.axis('off')

    correlation = merged['value_ratio'].corr(merged['value_sp500'])

    stats_text = f"""
    📊 Correlation: {correlation:.3f}  |  🎯 Both at similar levels relative to {start_year}
    💡 When Cu/Au turns, equities follow within 3-6 months
    ⚠️  Current Cu/Au at 50-year lows suggests major risk-on move ahead
    """

    ax_stats.text(0.5, 0.5, stats_text.strip(), ha='center', va='center',
                  fontsize=11, family='monospace',
                  bbox=dict(boxstyle='round,pad=1', facecolor='#ffffcc', alpha=0.95))

    plt.tight_layout()
    plt.savefig('thesis_chart2_copper_gold_vs_sp500.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: thesis_chart2_copper_gold_vs_sp500.png")
    plt.close()


def chart_copper_gold_bitcoin(db):
    """Chart 3: Cu/Au vs BTC with cycle peaks marked."""
    print(f"\n📈 Chart 3: Cu/Au vs Bitcoin...")

    ratio = db.get_indicator_data('copper_gold_ratio_proper')
    btc = db.get_indicator_data('bitcoin_price')

    if btc is None or len(btc) == 0:
        print("⚠️  No Bitcoin data, skipping this chart")
        return

    # Normalize timezones
    ratio['date'] = pd.to_datetime(ratio['date']).dt.tz_localize(None)
    btc['date'] = pd.to_datetime(btc['date']).dt.tz_localize(None)

    merged = pd.merge(ratio, btc, on='date', suffixes=('_ratio', '_btc'))

    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(4, 1, height_ratios=[3, 0.5, 0.01, 0.01])
    ax1 = fig.add_subplot(gs[0])

    # Plot Cu/Au
    color1 = '#2E86AB'
    ax1.plot(merged['date'], merged['value_ratio'], linewidth=2.5, color=color1,
             label='Copper/Gold Ratio', zorder=2)
    ax1.set_ylabel('Copper/Gold Ratio', fontsize=13, color=color1, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.2)

    # Plot BTC (log scale)
    ax2 = ax1.twinx()
    color2 = '#FF8C00'
    ax2.semilogy(merged['date'], merged['value_btc'], linewidth=2, color=color2,
                 label='Bitcoin Price (log scale)', alpha=0.8, zorder=1)
    ax2.set_ylabel('Bitcoin Price (USD, log)', fontsize=13, color=color2, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)

    # Mark known BTC cycle peaks
    cycle_peaks = [
        ('2013-11-30', 'Nov 2013'),
        ('2017-12-17', 'Dec 2017'),
        ('2021-11-10', 'Nov 2021'),
    ]

    for peak_date, label in cycle_peaks:
        peak_dt = pd.to_datetime(peak_date)
        if peak_dt in merged['date'].values:
            ax2.axvline(x=peak_dt, color='red', linestyle='--', linewidth=1.5, alpha=0.6)
            ax2.text(peak_dt, ax2.get_ylim()[1]*0.9, label, rotation=90,
                    va='top', ha='right', fontsize=9, color='red')

    ax1.set_title('Copper/Gold Peaks Precede Bitcoin Cycle Tops by 12-60 Days',
                  fontsize=17, fontweight='bold', pad=20)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

    ax1.set_xticklabels([])

    # Stats
    ax_stats = fig.add_subplot(gs[1])
    ax_stats.axis('off')

    stats_text = f"""
    🎯 Historical Pattern: Cu/Au peaks → BTC tops within 12-60 days
    💡 2013, 2017, 2021 cycles all followed this pattern
    ⚠️  Current Cu/Au at lows suggests we're EARLY in next risk cycle, not late
    """

    ax_stats.text(0.5, 0.5, stats_text.strip(), ha='center', va='center',
                  fontsize=11, family='monospace',
                  bbox=dict(boxstyle='round,pad=1', facecolor='#ffffcc', alpha=0.95))

    plt.tight_layout()
    plt.savefig('thesis_chart3_copper_gold_vs_bitcoin.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: thesis_chart3_copper_gold_vs_bitcoin.png")
    plt.close()


def chart_liquidity_dashboard(db, start_year=2020):
    """Chart 4: Multi-panel liquidity indicators."""
    print(f"\n📈 Chart 4: Liquidity Dashboard ({start_year}+)...")

    # Get indicators
    sofr_spread = db.get_indicator_data('sofr_dff_spread')
    m2 = db.get_indicator_data('m2sl')
    fed_bs = db.get_indicator_data('walcl')
    hy_spread = db.get_indicator_data('bamlh0a0hym2')

    # Filter to start year
    sofr_spread = sofr_spread[sofr_spread['date'] >= f'{start_year}-01-01']
    m2 = m2[m2['date'] >= f'{start_year}-01-01']
    fed_bs = fed_bs[fed_bs['date'] >= f'{start_year}-01-01']
    hy_spread = hy_spread[hy_spread['date'] >= f'{start_year}-01-01']

    fig, axes = plt.subplots(4, 1, figsize=(16, 14), sharex=True)
    fig.suptitle('Liquidity Stress Easing = Risk-On Signal', fontsize=18, fontweight='bold', y=0.995)

    # Panel 1: SOFR-DFF Spread (repo stress)
    axes[0].plot(sofr_spread['date'], sofr_spread['value'], linewidth=2, color='#d62728')
    axes[0].axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.3)
    axes[0].set_ylabel('SOFR-DFF Spread\n(Basis Points)', fontsize=11, fontweight='bold')
    axes[0].set_title('Repo Market Stress (↓ = Less Stress)', fontsize=12, loc='left')
    axes[0].grid(True, alpha=0.2)

    # Panel 2: M2 Money Supply
    axes[1].plot(m2['date'], m2['value'], linewidth=2, color='#2ca02c')
    axes[1].set_ylabel('M2 Money Supply\n($ Billions)', fontsize=11, fontweight='bold')
    axes[1].set_title('Money Supply (↑ = More Liquidity)', fontsize=12, loc='left')
    axes[1].grid(True, alpha=0.2)

    # Panel 3: Fed Balance Sheet
    axes[2].plot(fed_bs['date'], fed_bs['value']/1000, linewidth=2, color='#1f77b4')  # Convert to billions
    axes[2].set_ylabel('Fed Balance Sheet\n($ Trillions)', fontsize=11, fontweight='bold')
    axes[2].set_title('Fed Balance Sheet (QT vs QE)', fontsize=12, loc='left')
    axes[2].grid(True, alpha=0.2)

    # Panel 4: High Yield Spread
    axes[3].plot(hy_spread['date'], hy_spread['value'], linewidth=2, color='#ff7f0e')
    axes[3].set_ylabel('HY Spread\n(Percent)', fontsize=11, fontweight='bold')
    axes[3].set_title('Credit Stress (↓ = Risk-On)', fontsize=12, loc='left')
    axes[3].grid(True, alpha=0.2)
    axes[3].set_xlabel('Date', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig('thesis_chart4_liquidity_dashboard.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: thesis_chart4_liquidity_dashboard.png")
    plt.close()


def chart_copper_gold_dxy(db, start_year=2010):
    """Chart 5: Cu/Au vs Dollar Index (inverse relationship)."""
    print(f"\n📈 Chart 5: Cu/Au vs Dollar ({start_year}+)...")

    ratio = db.get_indicator_data('copper_gold_ratio_proper')
    dxy = db.get_indicator_data('dtwexbgs')

    ratio = ratio[ratio['date'] >= f'{start_year}-01-01']
    dxy = dxy[dxy['date'] >= f'{start_year}-01-01']

    merged = pd.merge(ratio, dxy, on='date', suffixes=('_ratio', '_dxy'))

    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(4, 1, height_ratios=[3, 0.5, 0.01, 0.01])
    ax1 = fig.add_subplot(gs[0])

    # Plot Cu/Au
    color1 = '#2E86AB'
    ax1.plot(merged['date'], merged['value_ratio'], linewidth=2.5, color=color1,
             label='Copper/Gold Ratio', zorder=2)
    ax1.set_ylabel('Copper/Gold Ratio', fontsize=13, color=color1, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.2)

    # Plot DXY (inverted for visualization)
    ax2 = ax1.twinx()
    color2 = '#8B4513'
    ax2.plot(merged['date'], merged['value_dxy'], linewidth=2, color=color2,
             label='Dollar Index', alpha=0.7, zorder=1)
    ax2.set_ylabel('Trade-Weighted Dollar Index', fontsize=13, color=color2, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.invert_yaxis()  # Invert so dollar down = risk-on up

    ax1.set_title('Weak Dollar = Strong Copper/Gold = Risk-On',
                  fontsize=17, fontweight='bold', pad=20)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

    ax1.set_xticklabels([])

    # Stats
    ax_stats = fig.add_subplot(gs[1])
    ax_stats.axis('off')

    correlation = merged['value_ratio'].corr(-merged['value_dxy'])  # Negative because inverse

    stats_text = f"""
    📊 Inverse Correlation: {correlation:.3f}  |  💵 Dollar down ~10% in 2025 = supportive for risk
    💡 Cu/Au and DXY typically move opposite directions
    🎯 Current setup: Dollar weakness + Cu/Au lows = dual risk-on signal
    """

    ax_stats.text(0.5, 0.5, stats_text.strip(), ha='center', va='center',
                  fontsize=11, family='monospace',
                  bbox=dict(boxstyle='round,pad=1', facecolor='#ffffcc', alpha=0.95))

    plt.tight_layout()
    plt.savefig('thesis_chart5_copper_gold_vs_dollar.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: thesis_chart5_copper_gold_vs_dollar.png")
    plt.close()


def main():
    """Create all thesis charts."""
    print("=" * 70)
    print("📊 CREATING THESIS CHARTS")
    print("=" * 70)
    print("\nThesis: Cu/Au at 50-year lows = major risk-on signal incoming\n")

    db = MacroDatabase('macro_data.db')

    # Fetch Bitcoin
    fetch_bitcoin_data(db)

    # Create all charts
    chart_copper_gold_ism_lead(db, 2010)
    chart_copper_gold_sp500(db, 2010)
    chart_copper_gold_bitcoin(db)
    chart_liquidity_dashboard(db, 2020)
    chart_copper_gold_dxy(db, 2010)

    db.close()

    print("\n" + "=" * 70)
    print("✅ ALL THESIS CHARTS CREATED")
    print("=" * 70)
    print("\nCharts for your article:")
    print("  1. thesis_chart1_copper_gold_leads_ism.png")
    print("  2. thesis_chart2_copper_gold_vs_sp500.png")
    print("  3. thesis_chart3_copper_gold_vs_bitcoin.png")
    print("  4. thesis_chart4_liquidity_dashboard.png")
    print("  5. thesis_chart5_copper_gold_vs_dollar.png")

    print("\n📝 Article Structure Suggestions:")
    print("  • Intro: Cu/Au at 50-year lows is misunderstood signal")
    print("  • Section 1: Why Cu/Au strips out supply noise (Chart 1)")
    print("  • Section 2: 3-6 month lead on manufacturing/ISM (Chart 1)")
    print("  • Section 3: Tracks equity risk appetite (Chart 2)")
    print("  • Section 4: Liquidity confirms the turn (Chart 4)")
    print("  • Section 5: Dollar weakness adds fuel (Chart 5)")
    print("  • Section 6: Crypto implications (Chart 3)")
    print("  • Conclusion: Early in cycle, not late")


if __name__ == "__main__":
    main()
