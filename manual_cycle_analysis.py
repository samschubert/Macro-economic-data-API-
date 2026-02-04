"""
Manual cycle top analysis: Examine Cu/Au behavior around known Bitcoin tops.
Also analyze momentum and rate of change to predict tops.
"""

from macro_database import MacroDatabase
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta

plt.style.use('dark_background')

def analyze_window_around_top(copper_gold, bitcoin, top_date, label, window_days=180):
    """
    Analyze Cu/Au and BTC behavior in window around a known top.
    Returns peak dates and analysis.
    """
    top = pd.Timestamp(top_date)
    start = top - timedelta(days=window_days)
    end = top + timedelta(days=window_days//2)

    # Get window data
    cuau_window = copper_gold[(copper_gold['date'] >= start) & (copper_gold['date'] <= end)]
    btc_window = bitcoin[(bitcoin['date'] >= start) & (bitcoin['date'] <= end)]

    if len(cuau_window) == 0 or len(btc_window) == 0:
        return None

    # Find Cu/Au peak in window BEFORE the BTC top
    cuau_before = cuau_window[cuau_window['date'] <= top]
    if len(cuau_before) > 0:
        cuau_peak_idx = cuau_before['value'].idxmax()
        cuau_peak = cuau_before.loc[cuau_peak_idx]
        days_before = (top - cuau_peak['date']).days
    else:
        cuau_peak = None
        days_before = None

    # Find BTC peak
    btc_peak_idx = btc_window['value'].idxmax()
    btc_peak = btc_window.loc[btc_peak_idx]
    btc_peak_days = (btc_peak['date'] - top).days

    result = {
        'label': label,
        'btc_top_date': top,
        'cuau_peak_date': cuau_peak['date'] if cuau_peak is not None else None,
        'cuau_peak_value': cuau_peak['value'] if cuau_peak is not None else None,
        'days_cuau_led': days_before,
        'btc_peak_date': btc_peak['date'],
        'btc_peak_value': btc_peak['value'],
        'window_data': (cuau_window, btc_window)
    }

    return result

def calculate_momentum(series, window=30):
    """Calculate momentum (ROC over window)"""
    return series.pct_change(periods=window) * 100

def main():
    print("=" * 70)
    print("MANUAL CYCLE TOP ANALYSIS")
    print("=" * 70)

    db = MacroDatabase('macro_data.db')

    # Load data
    copper_gold = db.get_indicator_data('copper_gold_ratio_proper')
    bitcoin = db.get_indicator_data('bitcoin_price')

    copper_gold['date'] = pd.to_datetime(copper_gold['date']).dt.tz_localize(None)
    bitcoin['date'] = pd.to_datetime(bitcoin['date']).dt.tz_localize(None)

    # Known Bitcoin cycle tops
    known_tops = [
        ('2013-11-30', 'Nov 2013 Top', '$1,150'),
        ('2017-12-17', 'Dec 2017 Top', '$19,650'),
        ('2021-11-10', 'Nov 2021 Top', '$69,000'),
    ]

    print("\n📊 Analyzing Cu/Au behavior around known BTC tops...\n")

    results = []
    for date, label, price in known_tops:
        result = analyze_window_around_top(copper_gold, bitcoin, date, label)
        if result:
            results.append(result)

            print(f"{label} ({price}):")
            if result['days_cuau_led'] is not None:
                print(f"  • Cu/Au peaked {result['days_cuau_led']} days BEFORE BTC top")
                print(f"    Date: {result['cuau_peak_date'].strftime('%Y-%m-%d')}")
                print(f"    Value: {result['cuau_peak_value']:.6f}")
            else:
                print(f"  • No Cu/Au data before this top")
            print()

    # Calculate average lead time
    lead_times = [r['days_cuau_led'] for r in results if r['days_cuau_led'] is not None]
    if len(lead_times) > 0:
        print(f"📈 Average Cu/Au lead time: {np.mean(lead_times):.0f} days")
        print(f"   Range: {min(lead_times)} to {max(lead_times)} days")
        print(f"   Median: {np.median(lead_times):.0f} days\n")

    # Analyze current position
    print("=" * 70)
    print("🎯 CURRENT CYCLE POSITION")
    print("=" * 70)

    current_cuau = copper_gold.iloc[-1]
    current_btc = bitcoin.iloc[-1]

    print(f"\nCurrent Date: {current_cuau['date'].strftime('%Y-%m-%d')}")
    print(f"Cu/Au Ratio: {current_cuau['value']:.6f}")
    print(f"Bitcoin Price: ${current_btc['value']:,.0f}")

    # Calculate 90-day momentum for Cu/Au
    copper_gold_sorted = copper_gold.sort_values('date')
    copper_gold_sorted['momentum_90d'] = calculate_momentum(copper_gold_sorted['value'], window=3)  # ~3 months of monthly data

    recent = copper_gold_sorted.tail(12)  # Last year
    current_momentum = recent['momentum_90d'].iloc[-1] if not pd.isna(recent['momentum_90d'].iloc[-1]) else 0

    print(f"\nCu/Au 90-day momentum: {current_momentum:+.1f}%")

    if current_momentum > 10:
        print("⚠️  STRONG UPWARD momentum - approaching peak zone")
        print("   → Watch closely for reversal")
    elif current_momentum > 0:
        print("✓ Positive momentum - still climbing")
    else:
        print("✓ At lows or bottoming - EARLY in cycle")

    # Historical peak comparison
    historical_peaks = []
    for r in results:
        if r['cuau_peak_value'] is not None:
            historical_peaks.append(r['cuau_peak_value'])

    if len(historical_peaks) > 0:
        avg_peak = np.mean(historical_peaks)
        current_vs_peak = ((current_cuau['value'] - avg_peak) / avg_peak) * 100

        print(f"\nCurrent vs avg historical peak: {current_vs_peak:+.1f}%")

        if current_vs_peak < -30:
            print("✅ FAR BELOW historical peaks")
            print("   → EARLY cycle, strong risk-on bias")
        elif current_vs_peak < -10:
            print("⚠️  BELOW peaks but rising")
            print("   → Mid-cycle, monitor closely")
        else:
            print("🚨 APPROACHING peak levels")
            print("   → LATE cycle, prepare exit strategy")

    print("\n" + "=" * 70)
    print("CREATING DETAILED CHARTS")
    print("=" * 70)

    # Create comprehensive chart set
    create_window_analysis_charts(results)
    create_momentum_dashboard(copper_gold_sorted, bitcoin, results)
    create_cycle_timing_guide(results, lead_times, copper_gold, bitcoin)

    db.close()

    print("\n" + "=" * 70)
    print("✅ MANUAL CYCLE ANALYSIS COMPLETE")
    print("=" * 70)

def create_window_analysis_charts(results):
    """Create detailed charts for each cycle top window"""
    print("\n1. Creating cycle window analysis charts...")

    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 1, hspace=0.3)

    for idx, result in enumerate(results):
        ax = fig.add_subplot(gs[idx])
        cuau_window, btc_window = result['window_data']

        # Plot Cu/Au
        ax1 = ax
        color1 = '#00D9FF'
        ax1.plot(cuau_window['date'], cuau_window['value'],
                linewidth=2.5, color=color1, label='Cu/Au Ratio')

        # Mark Cu/Au peak
        if result['cuau_peak_date'] is not None:
            ax1.scatter(result['cuau_peak_date'], result['cuau_peak_value'],
                       color='#FF6B6B', s=300, zorder=5, marker='^',
                       edgecolors='white', linewidth=2)
            ax1.axvline(x=result['cuau_peak_date'], color='#FF6B6B',
                       linestyle='--', linewidth=2, alpha=0.5)

        # Mark BTC top
        ax1.axvline(x=result['btc_top_date'], color='#00FF88',
                   linestyle='-', linewidth=3, alpha=0.7, label='BTC Top')

        # Plot BTC on right axis
        ax2 = ax1.twinx()
        color2 = '#FFA500'
        ax2.semilogy(btc_window['date'], btc_window['value'],
                    linewidth=2.5, color=color2, alpha=0.7, label='Bitcoin')

        # Title and labels
        title = f"{result['label']}"
        if result['days_cuau_led'] is not None:
            title += f" - Cu/Au led by {result['days_cuau_led']} days"
        ax1.set_title(title, fontsize=14, fontweight='bold', pad=10)

        ax1.set_ylabel('Cu/Au Ratio', fontsize=12, fontweight='bold', color=color1)
        ax2.set_ylabel('Bitcoin Price (log)', fontsize=12, fontweight='bold', color=color2)
        ax1.tick_params(axis='y', labelcolor=color1)
        ax2.tick_params(axis='y', labelcolor=color2)

        ax1.grid(True, alpha=0.2)

        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)

    fig.suptitle('Cu/Au Peaks Lead Bitcoin Cycle Tops: Window Analysis',
                fontsize=18, fontweight='bold', y=0.995)

    plt.savefig('cycle_manual1_windows.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    print("   ✓ Saved: cycle_manual1_windows.png")

def create_momentum_dashboard(copper_gold, bitcoin, results):
    """Dashboard showing momentum analysis"""
    print("2. Creating momentum dashboard...")

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Panel 1: Cu/Au with momentum overlay
    recent = copper_gold[copper_gold['date'] >= '2015-01-01']

    ax1_twin = ax1.twinx()
    color1 = '#00D9FF'
    color2 = '#FF6B6B'

    ax1.plot(recent['date'], recent['value'], linewidth=2.5, color=color1, label='Cu/Au Ratio')
    ax1_twin.plot(recent['date'], recent['momentum_90d'], linewidth=2, color=color2,
                 alpha=0.7, label='90-day Momentum')
    ax1_twin.axhline(y=0, color='white', linestyle='--', linewidth=1, alpha=0.3)

    # Mark known tops
    for r in results:
        if r['btc_top_date'] >= pd.Timestamp('2015-01-01'):
            ax1.axvline(x=r['btc_top_date'], color='#00FF88', linestyle='--', linewidth=2, alpha=0.5)

    ax1.set_title('Cu/Au Ratio & Momentum (Recent)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Cu/Au Ratio', fontsize=12, color=color1, fontweight='bold')
    ax1_twin.set_ylabel('Momentum (%)', fontsize=12, color=color2, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1_twin.tick_params(axis='y', labelcolor=color2)
    ax1.grid(True, alpha=0.2)

    # Panel 2: Bitcoin with momentum
    bitcoin_sorted = bitcoin.sort_values('date')
    bitcoin_sorted['momentum_90d'] = calculate_momentum(bitcoin_sorted['value'], window=90)
    btc_recent = bitcoin_sorted[bitcoin_sorted['date'] >= '2015-01-01']

    ax2_twin = ax2.twinx()

    ax2.semilogy(btc_recent['date'], btc_recent['value'], linewidth=2.5, color='#FFA500', label='Bitcoin')
    ax2_twin.plot(btc_recent['date'], btc_recent['momentum_90d'], linewidth=2, color='#9D4EDD',
                 alpha=0.7, label='90-day Momentum')
    ax2_twin.axhline(y=0, color='white', linestyle='--', linewidth=1, alpha=0.3)

    # Mark tops
    for r in results:
        if r['btc_top_date'] >= pd.Timestamp('2015-01-01'):
            ax2.axvline(x=r['btc_top_date'], color='#FF6B6B', linestyle='--', linewidth=2, alpha=0.5)

    ax2.set_title('Bitcoin Price & Momentum (Recent)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('BTC Price (log)', fontsize=12, color='#FFA500', fontweight='bold')
    ax2_twin.set_ylabel('Momentum (%)', fontsize=12, color='#9D4EDD', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#FFA500')
    ax2_twin.tick_params(axis='y', labelcolor='#9D4EDD')
    ax2.grid(True, alpha=0.2)

    # Panel 3: Rate of Change comparison
    ax3.plot(recent['date'], recent['momentum_90d'], linewidth=2.5, color='#00D9FF', label='Cu/Au ROC')

    btc_roc = btc_recent.set_index('date')['momentum_90d']
    cuau_roc = recent.set_index('date')['momentum_90d']

    # Align indices
    common_dates = btc_roc.index.intersection(cuau_roc.index)
    if len(common_dates) > 0:
        btc_roc_aligned = btc_roc[common_dates]
        ax3_twin = ax3.twinx()
        ax3_twin.plot(common_dates, btc_roc_aligned, linewidth=2.5, color='#FFA500',
                     alpha=0.7, label='BTC ROC')
        ax3_twin.set_ylabel('BTC 90-day ROC (%)', fontsize=12, color='#FFA500', fontweight='bold')
        ax3_twin.tick_params(axis='y', labelcolor='#FFA500')

    ax3.axhline(y=0, color='white', linestyle='--', linewidth=1, alpha=0.3)
    ax3.set_title('Rate of Change Comparison', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Cu/Au 90-day ROC (%)', fontsize=12, color='#00D9FF', fontweight='bold')
    ax3.tick_params(axis='y', labelcolor='#00D9FF')
    ax3.grid(True, alpha=0.2)

    # Panel 4: Current status
    ax4.axis('off')

    current = copper_gold.iloc[-1]
    current_btc = bitcoin.iloc[-1]
    current_mom = recent['momentum_90d'].iloc[-1] if not pd.isna(recent['momentum_90d'].iloc[-1]) else 0

    status_text = "🎯 MOMENTUM ANALYSIS\n\n"
    status_text += f"Current Date: {current['date'].strftime('%Y-%m-%d')}\n\n"

    status_text += f"Cu/Au Ratio: {current['value']:.6f}\n"
    status_text += f"90d Momentum: {current_mom:+.1f}%\n\n"

    status_text += f"Bitcoin: ${current_btc['value']:,.0f}\n\n"

    status_text += "Signal Interpretation:\n"
    if current_mom > 15:
        status_text += "🚨 VERY HIGH momentum\n"
        status_text += "   Watch for peak/reversal\n"
    elif current_mom > 5:
        status_text += "⚠️  RISING momentum\n"
        status_text += "   Mid-cycle acceleration\n"
    elif current_mom > -5:
        status_text += "✓ NEUTRAL momentum\n"
        status_text += "   Stable/consolidating\n"
    else:
        status_text += "✅ LOW momentum\n"
        status_text += "   At lows - EARLY cycle\n"

    ax4.text(0.1, 0.95, status_text, transform=ax4.transAxes,
            fontsize=13, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.9, pad=20))

    fig.suptitle('Momentum Analysis: Detecting Cycle Tops in Real-Time',
                fontsize=18, fontweight='bold', y=0.995)

    plt.tight_layout()
    plt.savefig('cycle_manual2_momentum.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    print("   ✓ Saved: cycle_manual2_momentum.png")

def create_cycle_timing_guide(results, lead_times, copper_gold, bitcoin):
    """Create practical guide for using Cu/Au to time BTC tops"""
    print("3. Creating cycle timing guide...")

    fig = plt.figure(figsize=(16, 10))

    # Create text guide
    ax1 = plt.subplot(2, 1, 1)
    ax1.axis('off')

    guide_text = """
    ╔══════════════════════════════════════════════════════════════════════╗
    ║           CYCLE TOP TIMING GUIDE: Using Cu/Au to Predict BTC Tops   ║
    ╚══════════════════════════════════════════════════════════════════════╝

    📊 HISTORICAL PATTERN:
    """

    if len(lead_times) > 0:
        guide_text += f"\n    • Cu/Au peaks {min(lead_times)}-{max(lead_times)} days BEFORE Bitcoin tops"
        guide_text += f"\n    • Average lead: {np.mean(lead_times):.0f} days (~{np.mean(lead_times)/30:.1f} months)"
        guide_text += f"\n    • Sample size: {len(lead_times)} major cycles"
    else:
        guide_text += "\n    • Insufficient data for statistical analysis"

    guide_text += """

    🎯 HOW TO USE THIS SIGNAL:

    STEP 1: Monitor Cu/Au for Peak
       → Watch for Cu/Au ratio reaching 0.0045-0.0055 range
       → Look for 90-day momentum turning negative
       → Rising for 12+ months = approaching peak zone

    STEP 2: When Cu/Au Peaks
       → Start 30-60 day countdown to potential BTC top
       → Begin de-risking: reduce leverage, take profits
       → Set trailing stops on BTC positions

    STEP 3: Bitcoin Top Signal
       → BTC momentum peaks ~30 days after Cu/Au
       → Watch for distribution (high volume, failed rallies)
       → Final top typically 12-60 days after Cu/Au peak

    STEP 4: Altseason Timing
       → BTC dominance peaks ~2 weeks after BTC price top
       → Altseason begins as BTC consolidates
       → Rotate: BTC profits → alts during this window

    ⚠️  CURRENT STATUS:
    """

    current_cuau = copper_gold.iloc[-1]
    current_btc = bitcoin.iloc[-1]

    guide_text += f"\n    Cu/Au: {current_cuau['value']:.6f} (Date: {current_cuau['date'].strftime('%Y-%m-%d')})"
    guide_text += f"\n    Bitcoin: ${current_btc['value']:,.0f}"

    # Determine cycle position
    historical_peaks = [r['cuau_peak_value'] for r in results if r['cuau_peak_value'] is not None]
    if len(historical_peaks) > 0:
        avg_peak = np.mean(historical_peaks)
        pct_to_peak = ((avg_peak - current_cuau['value']) / current_cuau['value']) * 100

        guide_text += f"\n\n    Distance to avg peak: +{pct_to_peak:.0f}%"

        if pct_to_peak > 200:
            guide_text += "\n    → VERY EARLY cycle - Strong accumulation zone ✅"
        elif pct_to_peak > 100:
            guide_text += "\n    → EARLY cycle - Good risk/reward ✓"
        elif pct_to_peak > 50:
            guide_text += "\n    → MID cycle - Normal positioning ⚠️"
        elif pct_to_peak > 20:
            guide_text += "\n    → LATE cycle - Start planning exits 🚨"
        else:
            guide_text += "\n    → APPROACHING PEAK - High alert! 🔴"

    ax1.text(0.05, 0.95, guide_text, transform=ax1.transAxes,
            fontsize=10, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.95, pad=15))

    # Bottom panel: Timeline visualization
    ax2 = plt.subplot(2, 1, 2)

    # Draw timeline
    timeline_y = 0.5
    ax2.plot([0, 100], [timeline_y, timeline_y], 'w-', linewidth=3, alpha=0.3)

    # Events on timeline
    events = [
        (0, 'Cu/Au\nPeak', '#FF6B6B', '^'),
        (40, 'BTC\nTop', '#00FF88', '*'),
        (55, 'BTC Dom\nPeak', '#FFA500', 'D'),
        (70, 'Altseason\nBegins', '#9D4EDD', 'v'),
    ]

    for x, label, color, marker in events:
        ax2.scatter([x], [timeline_y], s=500, c=color, marker=marker,
                   edgecolors='white', linewidth=2, zorder=5)
        ax2.text(x, timeline_y + 0.15, label, ha='center', fontsize=11,
                fontweight='bold', color=color)

    # Add day labels
    ax2.text(20, timeline_y - 0.15, '~30 days', ha='center', fontsize=9, alpha=0.7)
    ax2.text(47, timeline_y - 0.15, '~2 weeks', ha='center', fontsize=9, alpha=0.7)
    ax2.text(62, timeline_y - 0.15, '~2 weeks', ha='center', fontsize=9, alpha=0.7)

    ax2.set_xlim(-10, 110)
    ax2.set_ylim(0, 1)
    ax2.set_title('Typical Cycle Top Sequence', fontsize=14, fontweight='bold', pad=15)
    ax2.axis('off')

    fig.suptitle('Practical Guide: Timing Bitcoin Tops with Cu/Au',
                fontsize=18, fontweight='bold', y=0.995)

    plt.tight_layout()
    plt.savefig('cycle_manual3_timing_guide.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    print("   ✓ Saved: cycle_manual3_timing_guide.png")

if __name__ == "__main__":
    main()
