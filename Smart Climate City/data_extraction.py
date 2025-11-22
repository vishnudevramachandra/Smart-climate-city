"""
Data Extraction Module for Project EcoFlow
Connects to SensorBox database and extracts traffic and air quality data
"""

import psycopg2
import pandas as pd
from datetime import datetime
import os
from config import DB_CONFIG, TRAINING_DATA_MONTHS


def test_connection():
    """
    Test database connection via SSH tunnel.
    Returns True if successful, False otherwise.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Database connection successful!")
        print(f"📊 PostgreSQL version: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n⚠️  Make sure SSH tunnel is active:")
        print("ssh -N -p 2213 -L 15432:localhost:6543 hackathon2025@sensorbox.zapto.org")
        return False


def get_german_device_imei():
    """
    Identify the German device with historical traffic data.
    Returns the IMEI of the device with the most traffic data.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)

        # Find device with most traffic data (likely the German one with 1 year history)
        query = """
        SELECT
            t.imei,
            dm.friendly_name,
            dm.location_name,
            dm.latitude,
            dm.longitude,
            COUNT(*) as record_count,
            MIN(t.timestamp) as first_reading,
            MAX(t.timestamp) as last_reading
        FROM trafficsensordata t
        LEFT JOIN device_mapping dm ON t.imei = dm.imei
        WHERE t.tr1 IS NOT NULL AND t.tr2 IS NOT NULL
        GROUP BY t.imei, dm.friendly_name, dm.location_name, dm.latitude, dm.longitude
        ORDER BY record_count DESC
        LIMIT 5
        """

        df = pd.read_sql(query, conn)
        conn.close()

        print("\n📡 Top devices with traffic data:")
        print(df.to_string(index=False))
        print("\n")

        if len(df) > 0:
            german_imei = df.iloc[0]['imei']
            print(f"🇩🇪 Selected German device: {german_imei}")
            print(f"   Name: {df.iloc[0]['friendly_name']}")
            print(f"   Location: {df.iloc[0]['location_name']}")
            print(f"   Records: {df.iloc[0]['record_count']:,}")
            print(f"   Period: {df.iloc[0]['first_reading']} to {df.iloc[0]['last_reading']}")
            return german_imei
        else:
            print("❌ No traffic data found!")
            return None

    except Exception as e:
        print(f"❌ Error finding German device: {e}")
        return None


def get_german_traffic_data(imei, months=TRAINING_DATA_MONTHS):
    """
    Extract traffic data from the German device.

    Parameters:
    - imei: Device IMEI to query
    - months: Number of months of historical data (default from config)

    Returns:
    - pandas DataFrame with timestamp, tr1, tr2, and combined total
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)

        query = f"""
        SELECT
            timestamp,
            imei,
            tr1,
            tr2,
            (tr1 + tr2) as total_traffic
        FROM trafficsensordata
        WHERE imei = '{imei}'
          AND timestamp > NOW() - INTERVAL '{months} months'
          AND tr1 IS NOT NULL
          AND tr2 IS NOT NULL
        ORDER BY timestamp ASC
        """

        print(f"\n🔍 Extracting {months} months of traffic data for device {imei}...")
        df = pd.read_sql(query, conn)
        conn.close()

        print(f"✅ Extracted {len(df):,} traffic records")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"   Average traffic: {df['total_traffic'].mean():.1f} vehicles/interval")

        # Save to CSV
        os.makedirs('data_cache', exist_ok=True)
        csv_path = f'data_cache/german_traffic_{months}m.csv'
        df.to_csv(csv_path, index=False)
        print(f"💾 Saved to: {csv_path}")

        return df

    except Exception as e:
        print(f"❌ Error extracting traffic data: {e}")
        return None


def get_air_quality_statistics():
    """
    Extract air quality statistics from Italian devices to understand
    typical pollution levels and set thresholds.

    Returns:
    - pandas DataFrame with pollution statistics
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)

        query = """
        SELECT
            dm.location_name,
            dm.latitude,
            dm.longitude,
            COUNT(*) as reading_count,
            AVG(a.p10) as avg_pm10,
            MAX(a.p10) as max_pm10,
            AVG(a.p02) as avg_pm25,
            MAX(a.p02) as max_pm25,
            AVG(a.tmp) as avg_temp,
            AVG(a.hum) as avg_humidity
        FROM airqsensordata a
        JOIN device_mapping dm ON a.imei = dm.imei
        WHERE a.timestamp > NOW() - INTERVAL '1 month'
          AND dm.enabled = 1
          AND a.p10 IS NOT NULL
        GROUP BY dm.location_name, dm.latitude, dm.longitude
        ORDER BY avg_pm10 DESC
        """

        print("\n🌫️  Extracting air quality statistics from Italian devices...")
        df = pd.read_sql(query, conn)
        conn.close()

        print(f"✅ Analyzed {len(df)} locations")
        print(f"\n📊 Air Quality Summary:")
        print(f"   Average PM10: {df['avg_pm10'].mean():.1f} µg/m³")
        print(f"   Max PM10: {df['max_pm10'].max():.1f} µg/m³")
        print(f"   Average PM2.5: {df['avg_pm25'].mean():.1f} µg/m³")
        print(f"   Max PM2.5: {df['max_pm25'].max():.1f} µg/m³")

        # Save to CSV
        os.makedirs('data_cache', exist_ok=True)
        csv_path = 'data_cache/air_quality_stats.csv'
        df.to_csv(csv_path, index=False)
        print(f"💾 Saved to: {csv_path}")

        return df

    except Exception as e:
        print(f"❌ Error extracting air quality data: {e}")
        return None


def get_device_locations():
    """
    Get all device locations for map visualization.

    Returns:
    - pandas DataFrame with device locations
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)

        query = """
        SELECT
            imei,
            friendly_name,
            location_name,
            latitude,
            longitude
        FROM device_mapping
        WHERE enabled = 1
          AND latitude IS NOT NULL
          AND longitude IS NOT NULL
        ORDER BY friendly_name
        """

        df = pd.read_sql(query, conn)
        conn.close()

        print(f"\n📍 Found {len(df)} devices with GPS coordinates")

        return df

    except Exception as e:
        print(f"❌ Error extracting device locations: {e}")
        return None


if __name__ == "__main__":
    """
    Main execution: Test connection and extract all necessary data
    """
    print("=" * 70)
    print("🚦 PROJECT ECOFLOW - DATA EXTRACTION")
    print("=" * 70)

    # Step 1: Test connection
    print("\n[1/4] Testing database connection...")
    if not test_connection():
        print("\n❌ Exiting: Database connection failed")
        exit(1)

    # Step 2: Find German device
    print("\n[2/4] Identifying German device with traffic data...")
    german_imei = get_german_device_imei()
    if not german_imei:
        print("\n❌ Exiting: Could not find German device")
        exit(1)

    # Step 3: Extract traffic data
    print("\n[3/4] Extracting German traffic data...")
    traffic_data = get_german_traffic_data(german_imei)
    if traffic_data is None:
        print("\n❌ Exiting: Could not extract traffic data")
        exit(1)

    # Step 4: Extract air quality statistics
    print("\n[4/4] Extracting air quality statistics...")
    air_quality_data = get_air_quality_statistics()

    # Bonus: Get device locations
    print("\n[BONUS] Getting device locations for map...")
    locations = get_device_locations()
    if locations is not None:
        locations.to_csv('data_cache/device_locations.csv', index=False)

    print("\n" + "=" * 70)
    print("✅ DATA EXTRACTION COMPLETE!")
    print("=" * 70)
    print(f"\n📁 Data saved to: data_cache/")
    print(f"   - german_traffic_{TRAINING_DATA_MONTHS}m.csv")
    print(f"   - air_quality_stats.csv")
    print(f"   - device_locations.csv")
    print(f"\n🎯 Next step: Train the prediction model with: python model.py")
