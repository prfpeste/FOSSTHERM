# FOSSTHERM
Freie und quelloffene Soft- und Hardware für thermische Tischversuche

> **English summary:** This module is an Arduino-based benchtop experiment for determining the specific heat capacity of metal samples (aluminium, copper, steel) by water calorimetry. It includes 3D-printable parts, a KiCad schematic, Arduino firmware, a Python/Dash dashboard and an OpenModelica model. The documentation is written in German; source code and file names are in English.

## Projektziel

Das System wurde bewusst nicht als vollständig industrialisiertes Messsystem ausgelegt, sondern als leicht nachbaubare, offene und kostengünstige Plattform für den Einsatz in Lehre und Labor. Im Vordergrund stehen geringe Materialkosten, die Verwendung gut verfügbarer Standardbauteile, eine leicht nachvollziehbare Schaltungstopologie sowie die Möglichkeit, dass Studierende Module selbst aufbauen, anpassen und im Fehlerfall mit geringem Aufwand austauschen können.




## Lizenz

FOSSTHERM verwendet für verschiedene Teile des Projekts unterschiedliche Lizenzen:

- **Hardware und Konstruktionsdaten** im Verzeichnis `hardware/` unterliegen der Lizenz **CERN-OHL-W-2.0**.  
  Siehe `LICENSE-HARDWARE - CERN-OHL-W-2.0`.

- **Firmware und Software** in `firmware/` und `software/` unterliegen der Lizenz **GPL-3.0-or-later**.  
  Siehe `LICENSE-SOFTWARE - GPL-3.0`.

- **Dokumentation** in `docs/` unterliegt der Lizenz **CC-BY-SA-4.0**.  
  Siehe `LICENSE-DOCS - CC-BY-SA-4.0`.

Sofern nicht ausdrücklich anders angegeben, gelten für neue Dateien die Lizenzen ihres übergeordneten Verzeichnisses.
