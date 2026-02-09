#!/usr/bin/env python3
"""Migrate SGJobData.csv into a DuckDB database file at data/sg_jobs.duckdb

Usage:
    python scripts/migrate_to_duckdb.py
"""
import os
import sys

try:
    import duckdb
except Exception as e:
    print("duckdb package is required. Install with: pip install duckdb")
    raise

CSV = "SGJobData.csv"
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "sg_jobs.duckdb")

def main():
    if not os.path.exists(CSV):
        print(f"CSV file not found: {CSV}")
        sys.exit(1)

    os.makedirs(DB_DIR, exist_ok=True)

    # Connect to DuckDB file (will create if missing)
    conn = duckdb.connect(DB_PATH)
    try:
        # Create table from CSV; use read_csv_auto for best type inference
        print(f"Importing {CSV} into {DB_PATH} (table: sg_jobs)")
        conn.execute("CREATE TABLE IF NOT EXISTS sg_jobs AS SELECT * FROM read_csv_auto(?)", [CSV])
        print("Import complete.")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
