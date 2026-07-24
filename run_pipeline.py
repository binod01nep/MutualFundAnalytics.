"""
run_pipeline.py — Master Execution Script
==========================================
Runs the complete Bluestock Mutual Fund Analytics pipeline end-to-end:
  Step 1: Data Cleaning & SQLite DB Loading
  Step 2: Generate EDA Notebook
  Step 3: Generate Performance Analytics Notebook
  Step 4: Generate Advanced Analytics Notebook
  Step 5: Execute all three notebooks

Usage:
    python run_pipeline.py
"""

import subprocess
import sys
import os
import time

def run(cmd, description):
    """Run a shell command, print status, and exit on failure."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    start = time.time()
    result = subprocess.run(cmd, shell=True)
    elapsed = time.time() - start
    if result.returncode != 0:
        print(f"[FAILED] '{cmd}' exited with code {result.returncode}")
        sys.exit(result.returncode)
    print(f"[DONE] Completed in {elapsed:.1f}s")

def main():
    print("\n" + "="*60)
    print("  Bluestock MF Analytics — Full Pipeline")
    print("="*60)

    # Step 1: ETL and DB
    run("python data_cleaning.py", "Step 1: Data Cleaning & SQLite DB Loading")

    # Step 2-4: Build notebooks
    run("python build_eda.py", "Step 2: Building EDA Notebook")
    run("python build_performance_eda.py", "Step 3: Building Performance Analytics Notebook")
    run("python build_advanced_analytics.py", "Step 4: Building Advanced Analytics Notebook")

    # Step 5: Execute notebooks
    nb_cmd = "python -m jupyter nbconvert --to notebook --execute --inplace"
    run(f"{nb_cmd} notebooks/EDA_Analysis.ipynb", "Step 5a: Executing EDA_Analysis.ipynb")
    run(f"{nb_cmd} notebooks/Performance_Analytics.ipynb", "Step 5b: Executing Performance_Analytics.ipynb")
    run(f"{nb_cmd} notebooks/Advanced_Analytics.ipynb", "Step 5c: Executing Advanced_Analytics.ipynb")

    print("\n" + "="*60)
    print("  Pipeline Complete! All outputs generated successfully.")
    print("  - data/processed/  : Cleaned CSVs + scorecards")
    print("  - bluestock_mf.db  : SQLite Database")
    print("  - notebooks/       : Executed Jupyter Notebooks")
    print("  - reports/         : Charts (PNG)")
    print("\n  Run the dashboard with:")
    print("  python -m streamlit run dashboard/app.py")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
