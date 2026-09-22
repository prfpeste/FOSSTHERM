# Versuch: Wärmekapazität

Teil von [FOSSTHERM](../README.md) – freie und quelloffene thermische Tischversuche

> **English summary:** Arduino-based benchtop experiment for determining the specific heat capacity of metal samples (aluminium, copper, steel) by water calorimetry. This folder contains 3D-printable parts, a KiCad schematic, Arduino firmware, a Python/Dash dashboard and an OpenModelica model. The documentation is written in German; source code and file names are in English.

## Überblick

In diesem Versuch wird die **spezifische Wärmekapazität metallischer Proben** (Aluminium, Kupfer und Stahl) mittels **Wasserkalorimetrie** bestimmt. Die Probe wird mit Raumtemperatur in heißes Wasser getaucht; aus der Abkühlung des Wassers und der Erwärmung der Probe berechnet das Dashboard automatisch die Wärmekapazität.

Der Aufbau besteht aus:

- einem **Arduino Nano**,
- einem **DS18B20-Temperatursensor** für die Wassertemperatur,
- einem **MAX6675-Messverstärker mit Typ-K-Thermoelement** für die Probentemperatur,
- einem **Python-Dash-Dashboard** zur Live-Messwerterfassung und Berechnung der Wärmekapazität mit Wärmeverlustkorrektur,
- einem **digitalen Zwilling in OpenModelica** zur Simulation und Validierung sowie
- einer **vollständig 3D-druckbaren Mechanik**.

## Aufbau des Ordners

- `README.md`
  Diese Datei: Überblick, Ordneraufbau und Schnellstart.

- `01_Hardware/`
  - `BOM.ods`: Stückliste mit Bezugsquellen und 3D-Druckteilen.
  - `CAD_construction/STL/`: STL-Dateien aller 3D-druckbaren Teile (Grundplatte, Becherhalter, Deckel, Gehäuse, Kabelschellen, Tauchsiederhalterung, Probenhalter usw.).
  - `CAD_construction/test_cube.pdf`: Zeichnung des Probenwürfels.
  - `electrical_schematic/`: KiCad-Schaltplan (`PJ1_Tischversuch_Schaltplan.kicad_sch`) und als PDF exportierter Schaltplan.

- `02_Software/`
  - `Arduino/`: Firmware (`heat_capacity_sketch.ino`) und Liste der benötigten Bibliotheken (`libraries.txt`).
  - `Python/`: Dash-Anwendung (`HeatCapacity_python_code.py`) zur Live-Visualisierung, CSV-Export und Berechnung der Wärmekapazität, Hilfsskript zur Kalibrierung des Wärmeverlusts (`determine_heat_loss_coefficient.py`), Startskript für Linux/macOS (`run_HeatCapacity.sh`) sowie Beispielmessdaten in `data/`.
  - `Open_Modelica_simulation/`: Digitaler Zwilling des Kalorimetrieversuchs (`HeatCapacity_Experiment.mo`) zur Simulation und Validierung.

- `03_Documentation/`
  - `MANUAL.md`: Technisches Handbuch mit Theorie, Kalibrierung, Pinbelegung, Bedienungsanleitung, Sicherheitshinweisen und Fehlersuche.

## Schnellstart

### 1. Firmware

1. `02_Software/Arduino/heat_capacity_sketch.ino` in der Arduino-IDE öffnen.
2. Board **Arduino Nano** auswählen.
3. Über den Bibliotheksverwalter die benötigten Bibliotheken installieren: LiquidCrystal I2C, OneWire, DallasTemperature und MAX6675 (siehe `libraries.txt`).
4. Den richtigen Port wählen und den Sketch hochladen.

### 2. Python-Dashboard

```bash
git clone https://github.com/prfpeste/FOSSTHERM.git
cd FOSSTHERM/Waermekapazitaet/02_Software/Python
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Vor dem ersten Start in `HeatCapacity_python_code.py` die Konstante `SERIAL_PORT` an den seriellen Port des Arduino anpassen (voreingestellt ist `COM5`; unter Linux z. B. `/dev/ttyUSB0`, unter macOS z. B. `/dev/cu.usbserial-…`). Anschließend:

```bash
python HeatCapacity_python_code.py
```

Unter Linux/macOS kann alternativ `./run_HeatCapacity.sh` verwendet werden; das Skript legt die virtuelle Umgebung bei Bedarf selbst an.

Danach im Browser http://127.0.0.1:8050 öffnen, Wassermasse, Raumtemperatur und Probenmaterial eingeben und den Versuch starten. Den genauen Messablauf beschreibt das [Handbuch](03_Documentation/MANUAL.md).

### 3. Digitaler Zwilling (optional)

`02_Software/Open_Modelica_simulation/HeatCapacity_Experiment.mo` in OpenModelica (OMEdit) öffnen, um den Kalorimetrievorgang zu simulieren und mit einem aus dem Dashboard exportierten CSV-Datensatz zu vergleichen. Hinweise dazu stehen in der [README des Simulationsordners](02_Software/Open_Modelica_simulation/README.md).

## Voraussetzungen

- Python 3.10 oder neuer (siehe `02_Software/Python/requirements.txt`)
- Arduino-IDE 2.x mit Boardpaket für den Arduino Nano
- OpenModelica 1.22 oder neuer (nur für den digitalen Zwilling)

## Mitwirkende

#### Projektleitung und Betreuung

- Prof. Dr. Peter Stein

#### Entwicklung des Versuchs

- Marcel Yigitkurt
- Moritz Schubach

## Lizenz

Für die Bestandteile dieses Versuchs gelten die Lizenzen des FOSSTHERM-Repositorys; die Lizenztexte liegen im Hauptverzeichnis:

- **Hardware** (`01_Hardware/`: Schaltplan, 3D-Modelle, Zeichnungen, Stückliste) steht unter **CERN-OHL-W-2.0**.
  Siehe [`LICENSE-HARDWARE - CERN-OHL-W-2.0`](../LICENSE-HARDWARE%20-%20CERN-OHL-W-2.0).

- **Firmware und Software** (`02_Software/`: Arduino, Python, OpenModelica) stehen unter **GPL-3.0-or-later**.
  Siehe [`LICENSE-SOFTWARE - GPL-3.0`](../LICENSE-SOFTWARE%20-%20GPL-3.0).

- **Dokumentation** (`03_Documentation/` und die README-Dateien) steht unter **CC-BY-SA-4.0**.
  Siehe [`LICENSE-DOCS - CC-BY-SA-4.0`](../LICENSE-DOCS%20-%20CC-BY-SA-4.0).
