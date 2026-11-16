#!/usr/bin/env sh
# Launcher script for Linux and macOS (scrcpy-cpl)
DIR="$(cd "$(dirname "$0")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    exec python3 "$DIR/scrcpy_cpl.py" "$@"
elif command -v python >/dev/null 2>&1; then
    exec python "$DIR/scrcpy_cpl.py" "$@"
else
    echo "Error: python3 is not installed."
    echo "macOS : brew install python-tk"
    echo "Ubuntu: sudo apt install python3 python3-tk"
    exit 1
fi
