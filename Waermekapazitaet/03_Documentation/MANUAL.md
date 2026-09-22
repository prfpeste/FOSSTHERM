# FOSSTHERM – Wärmekapazität

## Technisches Handbuch und Bedienungsanleitung

Offene Kalorimetrie-Plattform zur Bestimmung der spezifischen Wärmekapazität fester Stoffe.

**Dokumentversion:** 1.1
**Lizenz:** CC-BY-SA-4.0

---

## 1. Theoretische Grundlagen und Energiebilanz

Ziel des Versuchs ist die Bestimmung der spezifischen Wärmekapazität $c_s$ fester Proben (Aluminium, Kupfer und Stahl) mit Hilfe der Wasserkalorimetrie.

Der Versuch beruht auf der Energieerhaltung zwischen dem heißen Wasser, dem Kalorimetergefäß und der zunächst kalten Metallprobe.

### 1.1 Energieerhaltung

Eine Metallprobe der Masse $m_s$ mit der Anfangstemperatur $T_s$ (etwa Raumtemperatur) wird in heißes Wasser der Masse $m_w$ mit der Anfangstemperatur $T_w$ (etwa 60 °C) getaucht. Wärme fließt vom Wasser in die Probe, bis sich die gemeinsame Mischtemperatur $T_m$ einstellt.

Ohne Wärmeverluste an die Umgebung gilt:

$$Q_\text{ab} = Q_\text{auf}$$

also

$$m_s \, c_s \, (T_m - T_s) = (m_w \, c_w + C_K) \, (T_w - T_m)$$

| Symbol | Bedeutung |
| :--- | :--- |
| $c_s$ | spezifische Wärmekapazität der Probe |
| $c_w$ | spezifische Wärmekapazität von Wasser (4,182 J/(g·K)) |
| $m_s$ | Masse der Probe |
| $m_w$ | Masse des Wassers |
| $C_K$ | effektive Wärmekapazität des Kalorimeters (in der Software `C_GEFAESS` = 50 J/K) |
| $T_s$, $T_w$ | Anfangstemperatur von Probe und Wasser |
| $T_m$ | Mischtemperatur |

Die Wärmekapazität des Kalorimeters umfasst die Beiträge von:

* doppelwandigem Glasgefäß,
* Temperatursensoren,
* mechanischen Bauteilen,
* weiteren wärmespeichernden Teilen.

Der Wert `C_GEFAESS` = 50 J/K ist ein Schätzwert. Er lässt sich bei Bedarf über einen Mischungsversuch mit kaltem und warmem Wasser experimentell bestimmen.

**Umsetzung in der Software:** Als Anfangstemperaturen verwendet das Dashboard den Mittelwert der ersten 10 Messwerte (ca. 5 s) nach dem Start, als Mischtemperatur den Mittelwert der Endtemperaturen von Wasser und Probe (jeweils die letzten 5 Messwerte). Daraus folgt für den Messablauf, dass die Probe erst einige Sekunden nach dem Start eingetaucht werden darf (siehe Abschnitt 6).

---

### 1.2 Wärmeverlustkorrektur

In der Realität tauscht das System Wärme mit der Umgebung aus, und zwar über:

* die Glaswände,
* die offene Wasseroberfläche,
* mechanische Verbindungen.

Deshalb ist eine Wärmeverlustkorrektur erforderlich. Der Verlustwärmestrom wird nach dem Newtonschen Abkühlungsgesetz proportional zur Temperaturdifferenz zwischen Wasser und Umgebung angesetzt:

$$\dot Q_V = K \, (T_w(t) - T_U)$$

mit

* $K$: Wärmeverlustkoeffizient des Aufbaus in W/K (in der Software `K_WERT`),
* $T_U$: Umgebungs- bzw. Raumtemperatur.

Die Software integriert diesen Verlust über die gesamte Messdauer:

$$Q_V = \int K \, (T_w(t) - T_U) \, dt$$

und korrigiert damit die Energiebilanz:

$$m_s \, c_s \, (T_m - T_s) = (m_w \, c_w + C_K) \, (T_w - T_m) - Q_V$$

Der Koeffizient $K$ wird einmalig aus einer Leer-Abkühlkurve ohne Probe bestimmt (siehe Abschnitt 2). Für das reine Abkühlen des Wassers gilt

$$(m_w \, c_w + C_K) \, \frac{dT}{dt} = -K \, (T - T_U)$$

Die Temperaturdifferenz zur Umgebung nimmt also exponentiell ab, mit der Abkühlkonstanten $k = K / (m_w \, c_w + C_K)$.

---

## 2. Kalibrierung des Systems

Eine neue Kalibrierung ist erforderlich, wenn:

* ein anderes Becherglas verwendet wird,
* sich die Wassermenge deutlich ändert,
* der mechanische Aufbau verändert wird,
* der Versuch unter deutlich anderen Umgebungsbedingungen durchgeführt wird.

Der aktuell hinterlegte Wert `K_WERT` = 0,185 W/K wurde aus der mitgelieferten Messung `02_Software/Python/data/measurement_heat_loss.csv` (300 g Wasser, Raumtemperatur 28,25 °C) bestimmt.

---

### 2.1 Aufnahme der Leer-Abkühlkurve

1. Das Becherglas mit ca. 300 g Wasser füllen (am besten wiegen).
2. Den Deckel mit dem Wassertemperatursensor aufsetzen.
3. Den Tauchsieder einsetzen und erst dann einschalten.
4. Das Wasser auf ca. 60 °C erwärmen.
5. Den Tauchsieder ausschalten und vom Netz trennen.
6. Das Wasser gründlich umrühren.
7. Das Thermoelement **ohne Probe** frei an der Luft neben dem Aufbau liegen lassen. Es misst so die Raumtemperatur mit, die später für die Auswertung verwendet wird.
8. Das Dashboard starten (Abschnitt 5), ein beliebiges Material auswählen (ohne Materialauswahl startet die Messung nicht) und auf **Versuch Starten** klicken.
9. Das System mindestens 30 Minuten ungestört abkühlen lassen. Die automatische Abschaltung greift bei dieser Messung nicht, weil Wasser- und Lufttemperatur weit auseinanderliegen. Die Messung daher mit **Stopp** beenden.
10. Mit **CSV Download** die Messdaten exportieren, die Datei in `measurement_heat_loss.csv` umbenennen und im Ordner `02_Software/Python/data/` ablegen.

---

### 2.2 Auswertung der Kalibrierung

Den Wärmeverlustkoeffizienten berechnet das Hilfsskript `determine_heat_loss_coefficient.py`. Es passt die Exponentialfunktion aus Abschnitt 1.2 an die Messdaten an. Im Ordner `02_Software/Python` aufrufen:

```bash
python determine_heat_loss_coefficient.py
```

Ohne weitere Angaben liest das Skript `data/measurement_heat_loss.csv`, nimmt 300 g Wasser an und verwendet den Mittelwert der Thermoelement-Spalte als Raumtemperatur. Abweichende Werte lassen sich übergeben:

```bash
python determine_heat_loss_coefficient.py data/measurement_heat_loss.csv --water-mass 280 --t-room 22.5
```

Den ausgegebenen Wert `K_WERT` in `HeatCapacity_python_code.py` im Abschnitt *KONFIGURATION* eintragen. Für den digitalen Zwilling kann derselbe Wert als Parameter `G_Isolation` im OpenModelica-Modell gesetzt werden.

---

## 3. Hardware

### 3.1 Hauptkomponenten

* **Mikrocontroller und Elektronik**
  * Arduino Nano im Elektronikgehäuse, Stromversorgung und Datenübertragung über USB
  * LCD-Anzeige 16×2 mit I²C-Adapter (Adresse 0x27) zur Live-Anzeige für die Betreuung
* **Temperatursensoren**
  * 1× digitaler Temperatursensor DS18B20 für die Wassertemperatur, mit 4,7-kΩ-Pull-up-Widerstand
  * Typ-K-Thermoelemente für die Probentemperatur, angeschlossen über einen MAX6675-Messverstärker. Laut Stückliste ist je Probenwürfel ein Thermoelement vorgesehen; über die Typ-K-Miniaturkupplung wird jeweils eines an den MAX6675 angeschlossen.
* **Wärmetechnik**
  * Tauchsieder (300 W, 230 V)
  * doppelwandiges Thermoglas (400 ml) als Kalorimetergefäß
* **Proben**
  * Würfel mit 35 mm Kantenlänge aus Aluminium (113 g), Kupfer (377 g) und Stahl (339 g) mit Bohrung für das Thermoelement (Zeichnung: `01_Hardware/CAD_construction/test_cube.pdf`)
* **Mechanik**
  * 3D-gedruckte Teile (Grundplatte, Becherhalter, Deckel, Kabelschellen, Gehäuse, Tauchsiederhalterung, Probenhalter)
* **Normteile**
  * M3-Linsenschrauben und -Muttern gemäß Stückliste

Die Probenmassen sind in der Software fest hinterlegt (`MATERIALS` in `HeatCapacity_python_code.py`). Werden eigene Proben gefertigt, müssen die Massen dort angepasst werden.

### 3.2 Pinbelegung

| Komponente | Signal | Arduino-Pin |
| :--- | :--- | :--- |
| DS18B20 (Wasser) | Daten (1-Wire) | D2 |
| MAX6675 (Probe) | SCK | D13 |
| MAX6675 (Probe) | CS | D10 |
| MAX6675 (Probe) | SO | D12 |
| LCD 16×2 (I²C) | SDA / SCL | A4 / A5 |

Der Arduino sendet alle 500 ms eine JSON-Zeile mit 9600 Baud über die serielle Schnittstelle, z. B. `{"t_water": 58.94, "t_sample": 28.50}`. Ein nicht angeschlossener Sensor wird als `null` übertragen.

### 3.3 Ablage im Repository

* **Stückliste:** `01_Hardware/BOM.ods`
* **3D-Druckteile (STL):** `01_Hardware/CAD_construction/STL/`
* **Zeichnung Probenwürfel:** `01_Hardware/CAD_construction/test_cube.pdf`
* **Schaltplan (KiCad und PDF):** `01_Hardware/electrical_schematic/`
* **Arduino-Firmware:** `02_Software/Arduino/`
* **Python-Auswertesoftware:** `02_Software/Python/` (Beispielmessdaten in `02_Software/Python/data/`)
* **Simulationsmodell:** `02_Software/Open_Modelica_simulation/`

---

## 4. Vorbereitung

1. Das Glasgefäß mit ca. 300 g Wasser füllen und die Masse möglichst genau bestimmen (Waage).
2. Die Raumtemperatur mit einem Referenzthermometer messen.
3. Den Aufbau vor direkter Sonneneinstrahlung und fremden Wärmequellen geschützt aufstellen.
4. Sicherstellen, dass die Probe Raumtemperatur hat.
5. Die Elektronikbox per USB mit dem Rechner verbinden.

---

## 5. Software starten

1. Beim ersten Mal in `HeatCapacity_python_code.py` die Konstante `SERIAL_PORT` an den seriellen Port des Arduino anpassen (Windows z. B. `COM5`, Linux z. B. `/dev/ttyUSB0`, macOS z. B. `/dev/cu.usbserial-…`).
2. Ein Terminal öffnen (z. B. Anaconda Prompt) und in den Python-Ordner wechseln:
   ```bash
   cd FOSSTHERM/Waermekapazitaet/02_Software/Python
   ```
3. Die benötigten Pakete installieren (nur beim ersten Mal):
   ```bash
   pip install -r requirements.txt
   ```
4. Das Dashboard starten:
   ```bash
   python HeatCapacity_python_code.py
   ```
   Unter Linux/macOS alternativ `./run_HeatCapacity.sh`.
5. Die im Terminal angezeigte Adresse (standardmäßig http://127.0.0.1:8050) im Browser öffnen.
6. Im Dashboard Wassermasse (g), Raumtemperatur (°C) und Probenmaterial eintragen bzw. auswählen.

---

## 6. Messablauf

1. Den Tauchsieder in das Wasser einsetzen, erst dann einschalten und das Wasser auf ca. 60 °C erwärmen.
2. Den Tauchsieder ausschalten und den Netzstecker ziehen.
3. Mit dem ausgeschalteten Tauchsieder vorsichtig umrühren, damit sich die Wassertemperatur ausgleicht, dann den Tauchsieder herausnehmen.
4. Das Thermoelementkabel der Probe durch den kleinen Deckeleinsatz führen und den Einsatz in die Hauptöffnung des Deckels setzen.
5. Im Dashboard auf **Versuch Starten** klicken, **ca. 5 Sekunden warten** und erst dann die Probe ins Wasser absenken. In diesen ersten Sekunden erfasst die Software die Anfangstemperaturen von Wasser und Probe.
6. Die Messung endet automatisch, sobald sich Wasser- und Probentemperatur 30 Sekunden lang um höchstens 1 °C unterscheiden. Mit **Stopp** lässt sie sich jederzeit auch manuell beenden.
7. Das Ergebnis prüfen. Angezeigt werden die gemessene spezifische Wärmekapazität in J/(g·K), der Literaturwert, die prozentuale Abweichung, die berücksichtigte Verlustwärme und eine Bewertung (Abweichung unter 15 %: „sehr gut“, unter 35 %: „brauchbar“, darüber: „große Abweichung“).
8. Bei Bedarf die Messdaten mit **CSV Download** exportieren (Datei `Messdaten.csv` mit den Spalten `zeit`, `temp_wasser`, `temp_wuerfel`). Das sollte vor einem neuen Start geschehen, da **Versuch Starten** die bisherigen Daten löscht.

---

## 7. Sicherheitshinweise

Der Versuch arbeitet mit heißem Wasser und einem netzbetriebenen Tauchsieder. Daher gilt:

* Heißes Wasser und erwärmte Proben nicht ohne Schutz berühren.
* Den Tauchsieder nur einschalten, wenn er vollständig im Wasser steht, und vor jeder Handhabung vom Netz trennen.
* Elektrische Komponenten trocken halten.
* Den Versuch nur unter Aufsicht durchführen.

---

## 8. Fehlersuche

### Keine Temperaturwerte (Anzeige „Kein Sensor“ im Dashboard, „---“ auf dem LCD)

* **Prüfen:**
  * USB-Verbindung und Stromversorgung des Arduino
  * Verdrahtung der Sensoren und 4,7-kΩ-Pull-up-Widerstand des DS18B20
  * Steckverbindung des Thermoelements
  * Einstellung `SERIAL_PORT` in `HeatCapacity_python_code.py`
  * ob noch ein anderes Programm (z. B. der serielle Monitor der Arduino-IDE) den Port belegt

### Unplausible Wärmekapazitätswerte

* **Mögliche Ursachen:**
  * nicht ausreichend umgerührt
  * Probe zu früh nach dem Start eingetaucht (Anfangstemperaturen falsch erfasst)
  * Probe hatte keine Raumtemperatur
  * falsch eingetragene Wassermasse oder Raumtemperatur
  * fehlende oder veraltete Wärmeverlustkalibrierung (`K_WERT`, siehe Abschnitt 2)

### Meldungen des Dashboards

* **„kein Gleichgewicht erreicht“:** Wasser und Probe lagen am Ende noch mehr als 1 °C auseinander, z. B. nach einem zu frühen manuellen Stopp. Versuch länger laufen lassen.
* **„Temperaturanstieg der Probe zu gering“:** Die Probe hat sich um weniger als 0,5 K erwärmt. Wassertemperatur und Zeitpunkt des Eintauchens prüfen.
* **„Energiebilanz negativ“:** Die berechnete Verlustwärme übersteigt die vom Wasser abgegebene Wärme. Meist war die Messung zu lang oder `K_WERT` passt nicht zum Aufbau.

### Unruhige Messwerte

* **Prüfen:**
  * lockere mechanische Verbindungen
  * fremde Wärmequellen in der Nähe
  * Kontakt des Thermoelements in der Probenbohrung

---

## 9. Lizenz

Diese Dokumentation ist Teil des Projekts FOSSTHERM und steht unter der Lizenz **CC-BY-SA-4.0** (siehe `LICENSE-DOCS - CC-BY-SA-4.0` im Hauptverzeichnis des Repositorys).
