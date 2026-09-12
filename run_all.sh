#!/usr/bin/env bash
# Runs the three verification scripts for the 3x3x3 DR Code paper.
set -e
PY=$(command -v python3 || command -v python) || {
  echo "Python was not found on PATH. Install Python 3.9 or later and try again." >&2
  exit 1
}
echo "============================================================"
echo " 1/3  verify_3d_recovery.py"
echo "============================================================"
"$PY" verify_3d_recovery.py
echo
echo "============================================================"
echo " 2/3  verify_3d_group.py"
echo "============================================================"
"$PY" verify_3d_group.py
echo
echo "============================================================"
echo " 3/3  verify_3d_round2.py"
echo "============================================================"
"$PY" verify_3d_round2.py
echo
echo "All verification scripts completed successfully."
