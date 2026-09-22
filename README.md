# FOSSTHERM

Freie und quelloffene Soft- und Hardware für thermische Tischversuche

> **English summary:** FOSSTHERM (Free and Open Source Thermal Experiments) is a collection of Arduino-based benchtop experiments for teaching heat transfer and thermodynamics. Each experiment lives in its own folder and includes hardware files (3D-printable parts, schematics, bill of materials), firmware, evaluation software and documentation. The documentation is written in German; source code and file names are in English.

## Projektziel

Das System wurde bewusst nicht als vollständig industrialisiertes Messsystem ausgelegt, sondern als leicht nachbaubare, offene und kostengünstige Plattform für den Einsatz in Lehre und Labor. Im Vordergrund stehen geringe Materialkosten, die Verwendung gut verfügbarer Standardbauteile, eine leicht nachvollziehbare Schaltungstopologie sowie die Möglichkeit, dass Studierende Module selbst aufbauen, anpassen und im Fehlerfall mit geringem Aufwand austauschen können.

Zusätzliche Maßnahmen zur Erhöhung der Robustheit, der EMV-Festigkeit oder für einen umfassenden Fehlerschutz wurden daher nur insoweit berücksichtigt, wie sie für den vorgesehenen Einsatz in beaufsichtigten Laborumgebungen erforderlich sind. Für Anwendungen in rauen Industrieumgebungen oder mit erhöhten Anforderungen an Zuverlässigkeit und Störfestigkeit sind weitergehende Schutz- und Schnittstellenbeschaltungen notwendig.

Die Versuche entstehen im Rahmen studentischer Projektarbeiten und richten sich an Hochschulen, Schulen und alle, die thermische Grundlagen anschaulich und messtechnisch nachvollziehbar vermitteln möchten.

## Versuche

| Versuch | Inhalt | Status |
| :--- | :--- | :--- |
| [Wärmekapazität](Waermekapazitaet/) | Bestimmung der spezifischen Wärmekapazität von Aluminium, Kupfer und Stahl mittels Wasserkalorimetrie | verfügbar |
| Wärmeleitfähigkeit | | in Arbeit |
| Tripelpunkt | | in Arbeit |
| Wärmetauscher | | in Arbeit |

Weitere Versuche werden ergänzt, sobald sie fertiggestellt sind.

## Aufbau des Repositorys

Jeder Versuch liegt in einem eigenen Unterordner mit einheitlicher Gliederung:

```
FOSSTHERM/
├── README.md                  Diese Datei
├── LICENSE-*                  Lizenztexte für Hardware, Software und Dokumentation
└── <Versuch>/
    ├── README.md              Überblick und Schnellstart zum Versuch
    ├── 01_Hardware/           Stückliste, 3D-Druckteile, Zeichnungen, Schaltplan
    ├── 02_Software/           Firmware, Auswertesoftware, Simulation
    └── 03_Documentation/      Handbuch mit Theorie, Bedienung und Sicherheitshinweisen
```

Die README im jeweiligen Versuchsordner beschreibt, welche Dateien im Einzelnen enthalten sind und wie der Versuch in Betrieb genommen wird.

## Mitwirkende

#### Projektleitung und Betreuung

- Prof. Dr. Peter Stein

Die an den einzelnen Versuchen beteiligten Studierenden sind in der README des jeweiligen Versuchsordners genannt.

## Verwandte Projekte

- [FOSSDAQ](https://github.com/prfpeste/FOSSDAQ) – freie und quelloffene modulare Messdatenerfassung für Lehre und Labor

## Lizenz

FOSSTHERM verwendet für verschiedene Teile des Projekts unterschiedliche Lizenzen:

- **Hardware und Konstruktionsdaten** in den Ordnern `01_Hardware/` der einzelnen Versuche unterliegen der Lizenz **CERN-OHL-W-2.0**.
  Siehe [`LICENSE-HARDWARE - CERN-OHL-W-2.0`](LICENSE-HARDWARE%20-%20CERN-OHL-W-2.0).

- **Firmware und Software** in den Ordnern `02_Software/` unterliegen der Lizenz **GPL-3.0-or-later**.
  Siehe [`LICENSE-SOFTWARE - GPL-3.0`](LICENSE-SOFTWARE%20-%20GPL-3.0).

- **Dokumentation** in den Ordnern `03_Documentation/` sowie die README-Dateien unterliegen der Lizenz **CC-BY-SA-4.0**.
  Siehe [`LICENSE-DOCS - CC-BY-SA-4.0`](LICENSE-DOCS%20-%20CC-BY-SA-4.0).

Sofern nicht ausdrücklich anders angegeben, gelten für neue Dateien die Lizenzen ihres übergeordneten Verzeichnisses.
