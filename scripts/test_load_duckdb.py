#!/usr/bin/env python3
import sys
from pathlib import Path

# Ensure project package path is on sys.path
base = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(base))

from sg_job_data_processor import JobDataProcessor

db_path = base / 'data' / 'sg_jobs.duckdb'
print('Testing DuckDB path:', db_path)
proc = JobDataProcessor(str(db_path))
print('Rows:', len(proc.df))
print('Columns sample:', list(proc.df.columns)[:10])
