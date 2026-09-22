#!/usr/bin/env bash
# In den Ordner dieses Skripts wechseln
cd "$(dirname "$0")"

# Virtuelle Umgebung aktivieren
if [ ! -d ".venv" ]; then
  echo "Virtuelle Umgebung .venv nicht gefunden. Erstelle sie..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

# Flask-App starten
python HeatCapacity_python_code.py
