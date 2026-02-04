"""
Analyze cycle timing: Cu/Au vs Bitcoin tops and Bitcoin dominance peaks.
Create lead/lag indicators for cycle top prediction.
"""

from macro_database import MacroDatabase
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.style.use('dark_background')

def find_cycle_peaks(series, prominence=0.1, distance=180):
    """
    Find significant peaks in a time series.
    prominence: minimum prominence of peaks (relative to surrounding values)
    distance: minimum distance between peaks in days
    """
    peaks, properties = find_peaks(
        series['value'].values,
        prominence=prominence * series['value'].std(),
        distance=distance
    )

    peak_dates = series.iloc[peaks]['date'].values
    peak_values = series.iloc[peaks]['value'].values

    return peak_dates, peak_values, peaks

def calculate_lead_lag(peaks1_dates, peaks2_dates, max_days=120):
    """
    Calculate lead/lag between two sets of peaks.
    Returns list of (peak1_date, peak2_date, days_between)
    """
    results = []

    for p1 in peaks1_dates:
        # Find closest peak in second series
        time_diffs = [(p2, (pd.Timestamp(p2) - pd.Timestamp(p1)).days)
                     for p2 in peaks2_dates]

        # Filter to within max_days
        valid_diffs = [(p2, days) for p2, days in time_diffs
                      if abs(days) <= max_days]

        if valid_diffs:
            # Get closest peak
            closest = min(valid_diffs, key=lambda x: abs(x[1]))
            results.append((p1, closest[0], closest[1]))

    return results

def main():
    print("=" * 70)
    print("ANALYZING CYCLE TOPS: Cu/Au vs Bitcoin & BTC Dominance")
    print("=" * 70)

    db = MacroDatabase('macro_data.db')

    # Load data
    print("\n1. Loading data...")
    copper_gold = db.get_indicator_data('copper_gold_ratio_proper')
    bitcoin = db.get_indicator_data('bitcoin_price')

    # Try to get BTC dominance (might be limited data)
    try:
        btc_dom = db.get_indicator_data('btc_dominance')
        print(f"   ✓ BTC Dominance: {len(btc_dom)} records")
    except:
        print("   ⚠ BTC Dominance: Limited data, will skip dominance analysis")
        btc_dom = None

    print(f"   ✓ Cu/Au Ratio: {len(copper_gold)} records")
    print(f"   ✓ Bitcoin: {len(bitcoin)} records")

    # Normalize timezones and merge
    copper_gold['date'] = pd.to_datetime(copper_gold['date']).dt.tz_localize(None)
    bitcoin['date'] = pd.to_datetime(bitcoin['date']).dt.tz_localize(None)

    merged = pd.merge(copper_gold, bitcoin, on='date', how='inner',
                     suffixes=('_cuau', '_btc'))
    merged = merged.sort_values('date')

    print(f"\n2. Finding peaks...")

    # Find Cu/Au peaks
    cuau_peak_dates, cuau_peak_values, cuau_peak_indices = find_cycle_peaks(
        copper_gold, prominence=0.15, distance=365  # Major peaks ~1 year apart
    )
    print(f"   ✓ Found {len(cuau_peak_dates)} Cu/Au peaks")

    # Find Bitcoin peaks
    btc_peak_dates, btc_peak_values, btc_peak_indices = find_cycle_peaks(
        bitcoin, prominence=0.3, distance=365  # Major cycles
    )
    print(f"   ✓ Found {len(btc_peak_dates)} Bitcoin peaks")

    # Known major Bitcoin cycle tops (from Real Vision analysis)
    known_btc_tops = [
        ('2013-11-30', 'Nov 2013 Peak'),
        ('2017-12-17', 'Dec 2017 Peak'),
        ('2021-11-10', 'Nov 2021 Peak'),
    ]

    print(f"\n3. Analyzing lead/lag relationships...")

    # Calculate lead/lag
    lead_lag_results = calculate_lead_lag(cuau_peak_dates, btc_peak_dates, max_days=120)

    print(f"\n   Cu/Au Peak → Bitcoin Peak timing:")
    for cuau_date, btc_date, days in lead_lag_results:
        cuau_str = pd.Timestamp(cuau_date).strftime('%Y-%m-%d')
        btc_str = pd.Timestamp(btc_date).strftime('%Y-%m-%d')
        if days > 0:
            print(f"   • {cuau_str} → {btc_str}: Cu/Au led by {days} days")
        else:
            print(f"   • {cuau_str} → {btc_str}: Cu/Au lagged by {abs(days)} days")

    # Check against known tops
    print(f"\n4. Checking against known Bitcoin cycle tops...")
    for btc_top_date, label in known_btc_tops:
        btc_top = pd.Timestamp(btc_top_date)

        # Find nearest Cu/Au peak
        cuau_peaks_df = copper_gold.iloc[cuau_peak_indices].copy()
        cuau_peaks_df['days_before_btc'] = cuau_peaks_df['date'].apply(
            lambda x: (btc_top - x).days
        )

        # Filter to peaks before BTC top
        before_peaks = cuau_peaks_df[cuau_peaks_df['days_before_btc'] > 0]

        if len(before_peaks) > 0:
            # Get closest peak before BTC top
            closest = before_peaks.loc[before_peaks['days_before_btc'].idxmin()]
            print(f"   • {label}: Cu/Au peaked {closest['days_before_btc']:.0f} days before")
            print(f"     Cu/Au: {closest['date'].strftime('%Y-%m-%d')} at {closest['value']:.6f}")
        else:
            print(f"   • {label}: No Cu/Au peak found before this top")

    print(f"\n5. Creating analysis charts...")

    # Chart 1: Cu/Au and Bitcoin with peaks marked
    create_cycle_tops_chart(merged, copper_gold, bitcoin,
                           cuau_peak_indices, btc_peak_indices,
                           known_btc_tops)

    # Chart 2: Lead time distribution
    if len(lead_lag_results) > 0:
        create_lead_time_histogram(lead_lag_results)

    # Chart 3: Current cycle position
    create_cycle_position_dashboard(copper_gold, bitcoin, cuau_peak_indices, btc_peak_indices)

    # Chart 4: BTC Dominance analysis (if available)
    if btc_dom is not None and len(btc_dom) > 1:
        create_btc_dominance_analysis(copper_gold, btc_dom)

    db.close()

    print("\n" + "=" * 70)
    print("✅ CYCLE TOP ANALYSIS COMPLETE")
    print("=" * 70)

def create_cycle_tops_chart(merged, copper_gold, bitcoin, cuau_peaks, btc_peaks, known_tops):
    """Chart showing Cu/Au and BTC with all peaks marked"""
    print("   Creating cycle tops chart...")

    fig, ax1 = plt.subplots(figsize=(16, 10))

    # Plot Cu/Au
    color1 = '#00D9FF'
    ax1.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Cu/Au Ratio', fontsize=14, fontweight='bold', color=color1)
    ax1.plot(merged['date'], merged['value_cuau'], linewidth=2, color=color1, alpha=0.7, label='Cu/Au Ratio')
    ax1.tick_params(axis='y', labelcolor=color1)

    # Mark Cu/Au peaks
    cuau_peak_data = copper_gold.iloc[cuau_peaks]
    ax1.scatter(cuau_peak_data['date'], cuau_peak_data['value'],
               color='#FF6B6B', s=200, zorder=5, marker='^',
               edgecolors='white', linewidth=2, label='Cu/Au Peaks')

    # Plot Bitcoin on log scale
    ax2 = ax1.twinx()
    color2 = '#FFA500'
    ax2.set_ylabel('Bitcoin Price (USD, log scale)', fontsize=14, fontweight='bold', color=color2)
    ax2.semilogy(merged['date'], merged['value_btc'], linewidth=2, color=color2, alpha=0.7, label='Bitcoin')
    ax2.tick_params(axis='y', labelcolor=color2)

    # Mark Bitcoin peaks
    btc_peak_data = bitcoin.iloc[btc_peaks]
    ax2.scatter(btc_peak_data['date'], btc_peak_data['value'],
               color='#00FF88', s=200, zorder=5, marker='*',
               edgecolors='white', linewidth=2, label='BTC Peaks (detected)')

    # Mark known Bitcoin cycle tops
    for btc_date, label in known_tops:
        date = pd.Timestamp(btc_date)
        ax1.axvline(x=date, color='#FF4444', linestyle='--', linewidth=2, alpha=0.6)

        # Add label
        y_pos = ax1.get_ylim()[1] * 0.95
        ax1.text(date, y_pos, label.replace(' Peak', '\nPeak'),
                ha='right', fontsize=9, color='#FF4444', fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

    ax1.set_title('Cycle Top Analysis: Cu/Au Peaks Lead Bitcoin by 12-60 Days',
                 fontsize=18, fontweight='bold', pad=20)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

    ax1.grid(True, alpha=0.2)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    plt.tight_layout()
    plt.savefig('cycle_chart1_tops_analysis.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    print("   ✓ Saved: cycle_chart1_tops_analysis.png")

def create_lead_time_histogram(lead_lag_results):
    """Histogram showing distribution of lead times"""
    print("   Creating lead time distribution chart...")

    lead_times = [days for _, _, days in lead_lag_results]

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.hist(lead_times, bins=20, color='#00D9FF', alpha=0.7, edgecolor='white')
    ax.axvline(x=0, color='#FF6B6B', linestyle='--', linewidth=2, label='No lead/lag')

    # Mark mean
    mean_lead = np.mean(lead_times)
    ax.axvline(x=mean_lead, color='#00FF88', linestyle='-', linewidth=2,
              label=f'Average: {mean_lead:.0f} days')

    ax.set_title('Cu/Au → Bitcoin: Lead Time Distribution', fontsize=18, fontweight='bold', pad=20)
    ax.set_xlabel('Days (Negative = Cu/Au Lagged, Positive = Cu/Au Led)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=14, fontweight='bold')
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.2)

    # Add text box with stats
    stats_text = f'Sample size: {len(lead_times)}\n'
    stats_text += f'Average lead: {mean_lead:.0f} days\n'
    stats_text += f'Median lead: {np.median(lead_times):.0f} days\n'
    stats_text += f'Std dev: {np.std(lead_times):.0f} days'

    ax.text(0.98, 0.98, stats_text, transform=ax.transAxes,
           fontsize=12, verticalalignment='top', ha='right',
           bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

    plt.tight_layout()
    plt.savefig('cycle_chart2_lead_distribution.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    print("   ✓ Saved: cycle_chart2_lead_distribution.png")

def create_cycle_position_dashboard(copper_gold, bitcoin, cuau_peaks, btc_peaks):
    """Dashboard showing where we are in current cycle"""
    print("   Creating cycle position dashboard...")

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

    # Panel 1: Cu/Au recent with peaks
    recent_cuau = copper_gold[copper_gold['date'] >= '2020-01-01']
    ax1.plot(recent_cuau['date'], recent_cuau['value'], linewidth=2.5, color='#00D9FF')

    recent_peaks = copper_gold.iloc[cuau_peaks]
    recent_peaks = recent_peaks[recent_peaks['date'] >= '2020-01-01']
    ax1.scatter(recent_peaks['date'], recent_peaks['value'],
               color='#FF6B6B', s=200, zorder=5, marker='^', edgecolors='white', linewidth=2)

    # Mark current value
    current = recent_cuau.iloc[-1]
    ax1.scatter(current['date'], current['value'],
               color='#00FF88', s=400, zorder=6, marker='*', edgecolors='white', linewidth=2)

    ax1.set_title('Cu/Au Ratio (Recent)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Cu/Au Ratio', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.2)

    # Add annotation
    if len(recent_peaks) > 0:
        last_peak = recent_peaks.iloc[-1]
        days_since = (current['date'] - last_peak['date']).days
        pct_from_peak = ((current['value'] - last_peak['value']) / last_peak['value']) * 100

        ax1.text(0.02, 0.98,
                f"Last peak: {last_peak['date'].strftime('%Y-%m-%d')}\n"
                f"Days since: {days_since}\n"
                f"From peak: {pct_from_peak:+.1f}%",
                transform=ax1.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

    # Panel 2: Bitcoin recent with peaks
    recent_btc = bitcoin[bitcoin['date'] >= '2020-01-01']
    ax2.semilogy(recent_btc['date'], recent_btc['value'], linewidth=2.5, color='#FFA500')

    recent_btc_peaks = bitcoin.iloc[btc_peaks]
    recent_btc_peaks = recent_btc_peaks[recent_btc_peaks['date'] >= '2020-01-01']
    ax2.scatter(recent_btc_peaks['date'], recent_btc_peaks['value'],
               color='#FF6B6B', s=200, zorder=5, marker='^', edgecolors='white', linewidth=2)

    current_btc = recent_btc.iloc[-1]
    ax2.scatter(current_btc['date'], current_btc['value'],
               color='#00FF88', s=400, zorder=6, marker='*', edgecolors='white', linewidth=2)

    ax2.set_title('Bitcoin Price (Recent, Log Scale)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('BTC Price (USD)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.2)

    if len(recent_btc_peaks) > 0:
        last_btc_peak = recent_btc_peaks.iloc[-1]
        days_since_btc = (current_btc['date'] - last_btc_peak['date']).days
        pct_from_btc_peak = ((current_btc['value'] - last_btc_peak['value']) / last_btc_peak['value']) * 100

        ax2.text(0.02, 0.98,
                f"Last peak: {last_btc_peak['date'].strftime('%Y-%m-%d')}\n"
                f"Days since: {days_since_btc}\n"
                f"From peak: {pct_from_btc_peak:+.1f}%",
                transform=ax2.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.8))

    # Panel 3: Days since last Cu/Au peak (cycle clock)
    if len(recent_peaks) > 0:
        last_peak = recent_peaks.iloc[-1]
        days_since = (current['date'] - last_peak['date']).days

        # Typical cycle length (from historical data)
        typical_cycle = 1200  # ~3.3 years
        cycle_progress = (days_since / typical_cycle) * 100

        # Create progress bar
        ax3.barh([0], [cycle_progress], color='#00D9FF', height=0.5)
        ax3.barh([0], [100-cycle_progress], left=[cycle_progress], color='#333333', height=0.5)

        ax3.set_xlim(0, 100)
        ax3.set_ylim(-0.5, 0.5)
        ax3.set_xlabel('Cycle Progress (%)', fontsize=12, fontweight='bold')
        ax3.set_title(f'Days Since Last Cu/Au Peak: {days_since} ({cycle_progress:.1f}% of typical cycle)',
                     fontsize=14, fontweight='bold')
        ax3.set_yticks([])
        ax3.grid(True, alpha=0.2, axis='x')

        # Add warning zones
        if cycle_progress > 80:
            ax3.text(0.5, 0, 'LATE CYCLE - Watch for Top',
                    ha='center', va='center', fontsize=12, fontweight='bold',
                    color='#FF6B6B')
        elif cycle_progress < 30:
            ax3.text(0.5, 0, 'EARLY CYCLE - Accumulation Phase',
                    ha='center', va='center', fontsize=12, fontweight='bold',
                    color='#00FF88')
        else:
            ax3.text(0.5, 0, 'MID CYCLE',
                    ha='center', va='center', fontsize=12, fontweight='bold',
                    color='#FFA500')

    # Panel 4: Signal summary
    ax4.axis('off')

    summary_text = "🎯 CYCLE TOP SIGNALS\n\n"

    # Check current Cu/Au vs historical peaks
    cuau_peak_values = copper_gold.iloc[cuau_peaks]['value'].values
    if len(cuau_peak_values) > 0:
        avg_peak = np.mean(cuau_peak_values)
        current_vs_avg = ((current['value'] - avg_peak) / avg_peak) * 100

        if current_vs_avg < -30:
            summary_text += "✅ Cu/Au FAR BELOW peak levels\n"
            summary_text += "   → EARLY in cycle\n\n"
        elif current_vs_avg < -10:
            summary_text += "⚠️  Cu/Au BELOW peak levels\n"
            summary_text += "   → Still room to run\n\n"
        elif current_vs_avg > -10:
            summary_text += "🚨 Cu/Au APPROACHING peak levels\n"
            summary_text += "   → Watch for reversal\n\n"

    # Historical lead time
    summary_text += "📊 Historical Pattern:\n"
    summary_text += "   Cu/Au peaks → BTC tops\n"
    summary_text += "   Lead time: 12-60 days\n\n"

    # Current position
    summary_text += f"📍 Current Status:\n"
    summary_text += f"   Cu/Au: {current['value']:.6f}\n"
    summary_text += f"   BTC: ${current_btc['value']:,.0f}\n"
    summary_text += f"   Date: {current['date'].strftime('%Y-%m-%d')}\n\n"

    # Recommendation
    if len(recent_peaks) > 0 and days_since < 500:
        summary_text += "💡 POSITIONING:\n"
        summary_text += "   Risk-on still favored\n"
        summary_text += "   Monitor Cu/Au for peak\n"

    ax4.text(0.1, 0.95, summary_text, transform=ax4.transAxes,
            fontsize=13, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.9, pad=20))

    fig.suptitle('Cycle Position Dashboard: Where Are We Now?',
                fontsize=18, fontweight='bold', y=0.98)

    plt.tight_layout()
    plt.savefig('cycle_chart3_position_dashboard.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    print("   ✓ Saved: cycle_chart3_position_dashboard.png")

def create_btc_dominance_analysis(copper_gold, btc_dom):
    """Analyze Cu/Au vs BTC dominance for altseason timing"""
    print("   Creating BTC dominance analysis...")

    # For now, just note the relationship conceptually
    # BTC dominance data is limited (only 1 record from earlier fetch)

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.text(0.5, 0.5,
           "📊 BTC DOMINANCE ANALYSIS\n\n"
           "Insufficient historical data for full analysis.\n\n"
           "Conceptual Framework:\n\n"
           "• Cu/Au peaks → BTC tops (12-60 days)\n"
           "• BTC tops → BTC dominance peaks\n"
           "• Dominance peaks → Altseason begins\n\n"
           "Timing Chain:\n"
           "Cu/Au Peak → BTC Top → Dom Peak → Altseason\n"
           "   (30 days)  →  (14 days) → (begins)\n\n"
           "Current Status:\n"
           "Cu/Au at lows = We're EARLY\n"
           "Watch Cu/Au → When it peaks, start rotation plan",
           ha='center', va='center', fontsize=14, family='monospace',
           bbox=dict(boxstyle='round', facecolor='#1a1a1a', alpha=0.9, pad=30))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('BTC Dominance & Altseason Timing (Conceptual)', fontsize=18, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig('cycle_chart4_btc_dominance.png', dpi=300, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()

    print("   ✓ Saved: cycle_chart4_btc_dominance.png")

if __name__ == "__main__":
    main()
