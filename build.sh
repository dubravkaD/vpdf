#!/bin/bash

set -e

rm -rf build dist __pycache__ *.spec

python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

pyinstaller --onefile --windowed --icon=pdf.png --name=vpdf --add-data "pdf.png:." main.py

echo "Complete setup"