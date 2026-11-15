#!/usr/bin/env sh
# Launcher script for Linux and macOS
DIR="$(cd "$(dirname "$0")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
    exec python3 "$DIR/scrcpy_launcher.py" "$@"
elif command -v python >/dev/null 2>&1; then
    exec python "$DIR/scrcpy_launcher.py" "$@"
else
    echo "Error: python3 belum terinstall."
    echo "macOS : brew install python-tk"
    echo "Ubuntu: sudo apt install python3 python3-tk"
    exit 1
fi
