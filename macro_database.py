"""
Macro Database Builder
A modular system for collecting, storing, and analyzing macroeconomic indicators.
Starts with the copper/gold ratio.

Requirements:
- Python 3.7+
- requests
- pandas
- matplotlib
- sqlite3 (built-in)

Usage:
    export FRED_API_KEY='your_api_key_here'
    python macro_database.py
"""

import os
import sqlite3
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FREDDataFetcher:
    """Handles all interactions with the FRED API."""

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FRED API fetcher.

        Args:
            api_key: FRED API key. If None, will try to get from FRED_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv('FRED_API_KEY')
        if not self.api_key:
            raise ValueError(
                "FRED API key required. Set FRED_API_KEY environment variable or pass api_key parameter.\n"
                "Get your API key from: https://fred.stlouisfed.org/docs/api/api_key.html"
            )

    def fetch_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch data for a specific FRED series.

        Args:
            series_id: FRED series identifier (e.g., 'GOLDAMGBD228NLBM')
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)

        Returns:
            DataFrame with 'date' and 'value' columns

        Raises:
            requests.RequestException: If API request fails
        """
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }

        if start_date:
            params['observation_start'] = start_date
        if end_date:
            params['observation_end'] = end_date

        try:
            logger.info(f"Fetching FRED series: {series_id}")
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if 'observations' not in data:
                raise ValueError(f"Unexpected response format for series {series_id}")

            observations = data['observations']

            # Convert to DataFrame
            df = pd.DataFrame(observations)
            df = df[['date', 'value']]

            # Clean data - remove missing values marked as '.'
            df = df[df['value'] != '.'].copy()
            df['value'] = pd.to_numeric(df['value'])
            df['date'] = pd.to_datetime(df['date'])

            logger.info(f"Successfully fetched {len(df)} observations for {series_id}")
            return df

        except requests.RequestException as e:
            logger.error(f"Failed to fetch FRED series {series_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing FRED data for {series_id}: {e}")
            raise


class MacroDatabase:
    """Manages the SQLite database for macroeconomic indicators."""

    def __init__(self, db_path: str = "macro_data.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
        logger.info(f"Connected to database: {db_path}")

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        cursor = self.conn.cursor()

        # Main indicators table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS macro_indicators (
                date TEXT NOT NULL,
                indicator_name TEXT NOT NULL,
                value REAL NOT NULL,
                PRIMARY KEY (date, indicator_name)
            )
        """)

        # Metadata table for tracking data sources
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS indicator_metadata (
                indicator_name TEXT PRIMARY KEY,
                source TEXT,
                series_id TEXT,
                description TEXT,
                last_updated TEXT
            )
        """)

        self.conn.commit()
        logger.info("Database tables initialized")

    def insert_indicator_data(
        self,
        indicator_name: str,
        data: pd.DataFrame,
        source: str = "FRED",
        series_id: Optional[str] = None,
        description: Optional[str] = None
    ):
        """
        Insert or update indicator data in the database.

        Args:
            indicator_name: Name of the indicator (e.g., 'copper_price')
            data: DataFrame with 'date' and 'value' columns
            source: Data source name
            series_id: Original series ID from source
            description: Description of the indicator
        """
        try:
            # Prepare data for insertion
            df = data.copy()
            df['indicator_name'] = indicator_name
            df.columns = ['date', 'value', 'indicator_name']
            df['date'] = df['date'].astype(str)

            # Delete existing records for this indicator to avoid duplicates
            cursor = self.conn.cursor()
            cursor.execute("""
                DELETE FROM macro_indicators
                WHERE indicator_name = ?
            """, (indicator_name,))

            # Insert data
            df.to_sql(
                'macro_indicators',
                self.conn,
                if_exists='append',
                index=False,
                method='multi'
            )

            # Update metadata
            cursor.execute("""
                INSERT OR REPLACE INTO indicator_metadata
                (indicator_name, source, series_id, description, last_updated)
                VALUES (?, ?, ?, ?, ?)
            """, (
                indicator_name,
                source,
                series_id,
                description,
                datetime.now().isoformat()
            ))

            self.conn.commit()
            logger.info(f"Inserted {len(df)} records for {indicator_name}")

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to insert data for {indicator_name}: {e}")
            raise

    def get_indicator_data(
        self,
        indicator_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieve indicator data from database.

        Args:
            indicator_name: Name of the indicator
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)

        Returns:
            DataFrame with date and value columns
        """
        query = """
            SELECT date, value
            FROM macro_indicators
            WHERE indicator_name = ?
        """
        params = [indicator_name]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date"

        df = pd.read_sql_query(query, self.conn, params=params)
        df['date'] = pd.to_datetime(df['date'])
        return df

    def calculate_ratio(
        self,
        numerator_indicator: str,
        denominator_indicator: str,
        ratio_name: str
    ) -> pd.DataFrame:
        """
        Calculate ratio between two indicators and store it.

        Args:
            numerator_indicator: Name of numerator indicator
            denominator_indicator: Name of denominator indicator
            ratio_name: Name for the calculated ratio

        Returns:
            DataFrame with the calculated ratio
        """
        # Get both datasets
        num_data = self.get_indicator_data(numerator_indicator)
        denom_data = self.get_indicator_data(denominator_indicator)

        # Merge on date
        merged = pd.merge(
            num_data,
            denom_data,
            on='date',
            suffixes=('_num', '_denom')
        )

        # Calculate ratio
        merged['value'] = merged['value_num'] / merged['value_denom']
        ratio_df = merged[['date', 'value']].copy()

        # Store the ratio
        self.insert_indicator_data(
            ratio_name,
            ratio_df,
            source='CALCULATED',
            description=f"Ratio of {numerator_indicator} to {denominator_indicator}"
        )

        logger.info(f"Calculated and stored ratio: {ratio_name}")
        return ratio_df

    def export_to_csv(
        self,
        output_path: str = "macro_data_export.csv",
        indicators: Optional[List[str]] = None
    ):
        """
        Export database to CSV format.

        Args:
            output_path: Path for output CSV file
            indicators: List of specific indicators to export (None = all)
        """
        query = "SELECT * FROM macro_indicators"
        params = []

        if indicators:
            placeholders = ','.join('?' * len(indicators))
            query += f" WHERE indicator_name IN ({placeholders})"
            params = indicators

        query += " ORDER BY indicator_name, date"

        df = pd.read_sql_query(query, self.conn, params=params)

        # Pivot to wide format for easier reading
        df_pivot = df.pivot(index='date', columns='indicator_name', values='value')
        df_pivot.to_csv(output_path)

        logger.info(f"Exported data to {output_path}")
        print(f"✓ Data exported to {output_path}")

    def close(self):
        """Close database connection."""
        self.conn.close()
        logger.info("Database connection closed")


class MacroVisualizer:
    """Handles visualization of macroeconomic data."""

    @staticmethod
    def plot_ratio_timeseries(
        data: pd.DataFrame,
        title: str = "Copper/Gold Ratio Over Time",
        ylabel: str = "Ratio",
        output_path: Optional[str] = None
    ):
        """
        Create a time series plot of a ratio.

        Args:
            data: DataFrame with 'date' and 'value' columns
            title: Plot title
            ylabel: Y-axis label
            output_path: If provided, save plot to this path
        """
        fig, ax = plt.subplots(figsize=(14, 7))

        ax.plot(data['date'], data['value'], linewidth=1.5, color='#2E86AB')
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3)

        # Add trend line
        z = np.polyfit(range(len(data)), data['value'], 1)
        p = np.poly1d(z)
        ax.plot(data['date'], p(range(len(data))),
                "--", color='#A23B72', alpha=0.7, label='Trend')

        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {output_path}")
            print(f"✓ Plot saved to {output_path}")

        # Show the plot interactively
        plt.show()

    @staticmethod
    def plot_multiple_indicators(
        db: MacroDatabase,
        indicators: List[str],
        title: str = "Macro Indicators",
        output_path: Optional[str] = None
    ):
        """
        Plot multiple indicators on the same chart (normalized).

        Args:
            db: MacroDatabase instance
            indicators: List of indicator names to plot
            title: Plot title
            output_path: If provided, save plot to this path
        """
        fig, ax = plt.subplots(figsize=(14, 7))

        for indicator in indicators:
            data = db.get_indicator_data(indicator)
            if len(data) > 0:
                # Normalize to 100 at start
                normalized = (data['value'] / data['value'].iloc[0]) * 100
                ax.plot(data['date'], normalized, label=indicator, linewidth=1.5)

        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Indexed to 100', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.xticks(rotation=45)
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {output_path}")
            print(f"✓ Plot saved to {output_path}")

        # Show the plot interactively
        plt.show()


def update_copper_gold_data(
    db: MacroDatabase,
    fetcher: FREDDataFetcher,
    start_date: Optional[str] = None
):
    """
    Update the database with latest copper and gold prices, and calculate ratio.

    Args:
        db: MacroDatabase instance
        fetcher: FREDDataFetcher instance
        start_date: Optional start date (YYYY-MM-DD). If None, fetches all available data.
    """
    print("\n📊 Updating macro database...")

    # Fetch copper prices
    # PCOPPUSDM: Global price of Copper (USD per metric ton)
    print("\n⏳ Fetching copper prices...")
    copper_data = fetcher.fetch_series('PCOPPUSDM', start_date=start_date)
    db.insert_indicator_data(
        'copper_price',
        copper_data,
        source='FRED',
        series_id='PCOPPUSDM',
        description='Global price of Copper (USD per metric ton)'
    )
    print(f"✓ Copper prices updated: {len(copper_data)} records")

    # Fetch gold prices
    # IR14270: Import Price Index for Nonmonetary Gold (index, not absolute price)
    print("\n⏳ Fetching gold prices...")
    gold_data = fetcher.fetch_series('IR14270', start_date=start_date)
    db.insert_indicator_data(
        'gold_price',
        gold_data,
        source='FRED',
        series_id='IR14270',
        description='Import Price Index (End Use): Nonmonetary Gold'
    )
    print(f"✓ Gold prices updated: {len(gold_data)} records")

    # Calculate copper/gold ratio
    print("\n⏳ Calculating copper/gold ratio...")
    ratio_data = db.calculate_ratio(
        'copper_price',
        'gold_price',
        'copper_gold_ratio'
    )
    print(f"✓ Copper/Gold ratio calculated: {len(ratio_data)} records")

    return ratio_data


def main():
    """Main execution function."""
    print("=" * 60)
    print("🏦 MACRO DATABASE BUILDER")
    print("=" * 60)

    # Check for API key
    api_key = os.getenv('FRED_API_KEY')
    if not api_key:
        print("\n❌ FRED API key not found!")
        print("\nTo get started:")
        print("1. Get your API key from: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("2. Set it as an environment variable:")
        print("   export FRED_API_KEY='your_api_key_here'")
        print("\nOr pass it directly in the code.")
        return

    try:
        # Initialize components
        fetcher = FREDDataFetcher(api_key)
        db = MacroDatabase("macro_data.db")

        # Update data (fetch all historical data on first run)
        ratio_data = update_copper_gold_data(db, fetcher)

        # Export to CSV
        print("\n⏳ Exporting data to CSV...")
        db.export_to_csv("macro_data_export.csv")

        # Visualize
        print("\n⏳ Creating visualizations...")
        import numpy as np  # Import here for the trend line
        MacroVisualizer.plot_ratio_timeseries(
            ratio_data,
            title="Copper/Gold Ratio Over Time",
            ylabel="Copper Price / Gold Price",
            output_path="copper_gold_ratio.png"
        )

        # Print summary statistics
        print("\n" + "=" * 60)
        print("📈 SUMMARY STATISTICS - Copper/Gold Ratio")
        print("=" * 60)
        print(f"Records: {len(ratio_data)}")
        print(f"Date range: {ratio_data['date'].min().date()} to {ratio_data['date'].max().date()}")
        print(f"Current ratio: {ratio_data['value'].iloc[-1]:.4f}")
        print(f"Average ratio: {ratio_data['value'].mean():.4f}")
        print(f"Min ratio: {ratio_data['value'].min():.4f} ({ratio_data.loc[ratio_data['value'].idxmin(), 'date'].date()})")
        print(f"Max ratio: {ratio_data['value'].max():.4f} ({ratio_data.loc[ratio_data['value'].idxmax(), 'date'].date()})")
        print("=" * 60)

        print("\n✅ Database update complete!")
        print(f"\n💾 Database location: macro_data.db")
        print(f"📊 CSV export: macro_data_export.csv")
        print(f"📈 Chart: copper_gold_ratio.png")

        # Close database
        db.close()

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
