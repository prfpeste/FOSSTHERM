"""Bestimmt den Waermeverlustkoeffizienten K (in W/K) aus einer Leer-Abkuehlkurve.

Modell (Newtonsche Abkuehlung):
    (m_w * c_w + C_K) * dT/dt = -K * (T - T_U)
    =>  ln(T - T_U) = ln(T0 - T_U) - k * t   mit  k = K / (m_w * c_w + C_K)

k wird per linearer Regression von ln(T - T_U) ueber t bestimmt.
Den Ergebniswert als K_WERT in HeatCapacity_python_code.py eintragen.

Aufruf (aus dem Ordner 02_Software/Python):
    python determine_heat_loss_coefficient.py
    python determine_heat_loss_coefficient.py data/measurement_heat_loss.csv --t-room 22.5 --water-mass 300

Ohne --t-room wird die Raumtemperatur als Mittelwert der Spalte
temp_wuerfel verwendet (Thermoelement liegt bei der Leermessung an der Luft).
"""

import argparse

import numpy as np
import pandas as pd

C_WATER = 4.182  # J/(g*K), wie in HeatCapacity_python_code.py


def main():
    parser = argparse.ArgumentParser(description="Waermeverlustkoeffizient K aus Leer-Abkuehlkurve bestimmen")
    parser.add_argument("csv", nargs="?", default="data/measurement_heat_loss.csv",
                        help="CSV-Export des Dashboards (Spalten zeit, temp_wasser, temp_wuerfel)")
    parser.add_argument("--water-mass", type=float, default=300.0, help="Wassermasse in g (Standard: 300)")
    parser.add_argument("--c-vessel", type=float, default=50.0,
                        help="Waermekapazitaet des Kalorimeters C_GEFAESS in J/K (Standard: 50)")
    parser.add_argument("--t-room", type=float, default=None,
                        help="Raumtemperatur in °C (Standard: Mittelwert der Spalte temp_wuerfel)")
    args = parser.parse_args()

    df = pd.read_csv(args.csv).dropna(subset=["zeit", "temp_wasser"])

    if args.t_room is not None:
        t_room = args.t_room
        source = "vorgegeben"
    else:
        t_room = df["temp_wuerfel"].dropna().mean()
        source = "Mittelwert temp_wuerfel"

    delta = df["temp_wasser"] - t_room
    valid = delta > 1.0  # nur Punkte deutlich oberhalb der Raumtemperatur verwenden
    if valid.sum() < 10:
        raise SystemExit("Zu wenige Messpunkte oberhalb der Raumtemperatur - Messung oder --t-room pruefen.")

    t = df.loc[valid, "zeit"].to_numpy()
    y = np.log(delta[valid].to_numpy())
    slope, _ = np.polyfit(t, y, 1)
    k = -slope  # 1/s

    c_total = args.water_mass * C_WATER + args.c_vessel  # J/K
    k_value = k * c_total  # W/K

    print(f"Messdauer:            {t[-1] - t[0]:.0f} s ({len(t)} Messpunkte)")
    print(f"Raumtemperatur:       {t_room:.2f} °C ({source})")
    print(f"Abkuehlkonstante k:   {k:.3e} 1/s (Zeitkonstante {1 / k / 60:.0f} min)")
    print(f"Waermekapazitaet ges: {c_total:.0f} J/K")
    print(f"K_WERT =              {k_value:.3f} W/K")


if __name__ == "__main__":
    main()
