"""
Regenerate all charts with stats box at the bottom (no overlap).
Best practice: Stats should be below the chart, not overlapping data.
"""

from macro_database import MacroDatabase
import matplotlib.pyplot as plt
import numpy as np


def create_ratio_chart_full(db):
    """Create full history copper/gold ratio chart."""
    print("\n📈 Creating Copper/Gold Ratio chart (full history)...")

    ratio_data = db.get_indicator_data('copper_gold_ratio_proper')

    if len(ratio_data) == 0:
        print("❌ No data found")
        return

    fig = plt.figure(figsize=(14, 9))
    gs = fig.add_gridspec(4, 1, height_ratios=[3, 0.5, 0.01, 0.01])
    ax = fig.add_subplot(gs[0])

    # Plot data
    ax.plot(ratio_data['date'], ratio_data['value'], linewidth=1.5, color='#2E86AB', label='Copper/Gold Ratio')
    ax.set_title('Copper/Gold Price Ratio Over Time', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Ratio (USD/lb ÷ USD/oz)', fontsize=12)
    ax.grid(True, alpha=0.3)

    # Trend line
    z = np.polyfit(range(len(ratio_data)), ratio_data['value'], 1)
    p = np.poly1d(z)
    ax.plot(ratio_data['date'], p(range(len(ratio_data))),
            "--", color='#A23B72', alpha=0.7, label='Trend', linewidth=1.5)

    ax.legend(loc='upper right')
    ax.set_xticklabels([])  # Remove x-axis labels from main chart

    # Stats table at bottom
    ax_stats = fig.add_subplot(gs[1])
    ax_stats.axis('off')

    current = ratio_data['value'].iloc[-1]
    avg = ratio_data['value'].mean()
    min_val = ratio_data['value'].min()
    max_val = ratio_data['value'].max()

    stats_text = f"""
    Current: {current:.6f}  |  Average: {avg:.6f}  |  Min: {min_val:.6f}  |  Max: {max_val:.6f}
    Date Range: {ratio_data['date'].min().date()} to {ratio_data['date'].max().date()}  |  Records: {len(ratio_data)}
    """

    ax_stats.text(0.5, 0.5, stats_text.strip(), ha='center', va='center',
                  fontsize=10, family='monospace',
                  bbox=dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.9))

    plt.tight_layout()
    plt.savefig('copper_gold_ratio_PROPER.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: copper_gold_ratio_PROPER.png")
    plt.close()


def create_ratio_chart_2012(db):
    """Create 2012-present copper/gold ratio chart."""
    print("\n📈 Creating Copper/Gold Ratio chart (2012-present)...")

    ratio_data = db.get_indicator_data('copper_gold_ratio_proper')
    ratio_data = ratio_data[ratio_data['date'] >= '2012-01-01'].copy()

    if len(ratio_data) == 0:
        print("❌ No data found")
        return

    fig = plt.figure(figsize=(14, 9))
    gs = fig.add_gridspec(4, 1, height_ratios=[3, 0.5, 0.01, 0.01])
    ax = fig.add_subplot(gs[0])

    # Plot data
    ax.plot(ratio_data['date'], ratio_data['value'], linewidth=2, color='#2E86AB', label='Copper/Gold Ratio')
    ax.set_title('Copper/Gold Price Ratio (2012-Present)', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Ratio (USD/lb ÷ USD/oz)', fontsize=12)
    ax.grid(True, alpha=0.3)

    # Trend line
    x_vals = range(len(ratio_data))
    z = np.polyfit(x_vals, ratio_data['value'], 1)
    p = np.poly1d(z)
    ax.plot(ratio_data['date'], p(x_vals),
            "--", color='#A23B72', alpha=0.7, label='Trend (2012-present)', linewidth=2)

    ax.legend(loc='upper right')
    ax.set_xticklabels([])

    # Stats table at bottom
    ax_stats = fig.add_subplot(gs[1])
    ax_stats.axis('off')

    current = ratio_data['value'].iloc[-1]
    avg = ratio_data['value'].mean()
    min_val = ratio_data['value'].min()
    max_val = ratio_data['value'].max()

    stats_text = f"""
    Current: {current:.6f}  |  Average: {avg:.6f}  |  Min: {min_val:.6f}  |  Max: {max_val:.6f}
    Date Range: {ratio_data['date'].min().date()} to {ratio_data['date'].max().date()}  |  Records: {len(ratio_data)}
    """

    ax_stats.text(0.5, 0.5, stats_text.strip(), ha='center', va='center',
                  fontsize=10, family='monospace',
                  bbox=dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.9))

    plt.tight_layout()
    plt.savefig('copper_gold_ratio_2012_onwards.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: copper_gold_ratio_2012_onwards.png")
    plt.close()


def create_copper_chart(db):
    """Create copper price chart."""
    print("\n📈 Creating Copper Price chart...")

    copper_data = db.get_indicator_data('copper_price_usd_lb')

    if len(copper_data) == 0:
        print("❌ No data found")
        return

    fig = plt.figure(figsize=(14, 9))
    gs = fig.add_gridspec(4, 1, height_ratios=[3, 0.5, 0.01, 0.01])
    ax = fig.add_subplot(gs[0])

    # Plot data
    ax.plot(copper_data['date'], copper_data['value'], linewidth=1.5, color='#CD7F32')
    ax.set_title('Copper Price Over Time', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Price (USD per pound)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xticklabels([])

    # Stats table at bottom
    ax_stats = fig.add_subplot(gs[1])
    ax_stats.axis('off')

    current = copper_data['value'].iloc[-1]
    avg = copper_data['value'].mean()
    min_val = copper_data['value'].min()
    max_val = copper_data['value'].max()

    stats_text = f"""
    Current: ${current:.4f}/lb  |  Average: ${avg:.4f}/lb  |  Min: ${min_val:.4f}/lb  |  Max: ${max_val:.4f}/lb
    Date Range: {copper_data['date'].min().date()} to {copper_data['date'].max().date()}  |  Records: {len(copper_data)}
    """

    ax_stats.text(0.5, 0.5, stats_text.strip(), ha='center', va='center',
                  fontsize=10, family='monospace',
                  bbox=dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.9))

    plt.tight_layout()
    plt.savefig('copper_price_per_lb.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: copper_price_per_lb.png")
    plt.close()


def create_gold_chart(db):
    """Create gold price chart."""
    print("\n📈 Creating Gold Price chart...")

    gold_data = db.get_indicator_data('gold_price_usd_oz')

    if len(gold_data) == 0:
        print("❌ No data found")
        return

    fig = plt.figure(figsize=(14, 9))
    gs = fig.add_gridspec(4, 1, height_ratios=[3, 0.5, 0.01, 0.01])
    ax = fig.add_subplot(gs[0])

    # Plot data
    ax.plot(gold_data['date'], gold_data['value'], linewidth=1.5, color='#FFD700')
    ax.set_title('Gold Price Over Time', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Price (USD per troy ounce)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xticklabels([])

    # Stats table at bottom
    ax_stats = fig.add_subplot(gs[1])
    ax_stats.axis('off')

    current = gold_data['value'].iloc[-1]
    avg = gold_data['value'].mean()
    min_val = gold_data['value'].min()
    max_val = gold_data['value'].max()

    stats_text = f"""
    Current: ${current:.2f}/oz  |  Average: ${avg:.2f}/oz  |  Min: ${min_val:.2f}/oz  |  Max: ${max_val:.2f}/oz
    Date Range: {gold_data['date'].min().date()} to {gold_data['date'].max().date()}  |  Records: {len(gold_data)}
    """

    ax_stats.text(0.5, 0.5, stats_text.strip(), ha='center', va='center',
                  fontsize=10, family='monospace',
                  bbox=dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.9))

    plt.tight_layout()
    plt.savefig('gold_price_per_oz.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: gold_price_per_oz.png")
    plt.close()


def main():
    """Regenerate all charts with stats at bottom."""
    print("=" * 70)
    print("📊 REGENERATING ALL CHARTS (Stats at Bottom)")
    print("=" * 70)

    db = MacroDatabase('macro_data.db')

    create_ratio_chart_full(db)
    create_ratio_chart_2012(db)
    create_copper_chart(db)
    create_gold_chart(db)

    db.close()

    print("\n" + "=" * 70)
    print("✅ ALL CHARTS REGENERATED")
    print("=" * 70)
    print("\nCharts now have stats boxes at the bottom (no overlap).")
    print("Refresh your dashboard to see the updated charts!")
    print("\n📊 Dashboard: file:///Users/samschubert/macro_dashboard.html")


if __name__ == "__main__":
    main()
