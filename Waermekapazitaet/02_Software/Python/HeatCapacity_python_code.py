import sys
import subprocess

# --- AUTO-INSTALLER ---
try:
    import pandas as pd
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas'])
    import pandas as pd

import threading
import time
import json
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import serial

# =========================================================
# KONFIGURATION
# =========================================================

SERIAL_PORT = 'COM5'
BAUD_RATE = 9600

# Apparatekonstante (Becher + Sensoren)
C_GEFAESS = 50     # J/K

# Kalibrierter Waermeverlustkoeffizient
# Ermittelt aus der Leer-Abkuehlkurve data/measurement_heat_loss.csv (Raumtemperatur 28.25 °C),
# Neuberechnung mit determine_heat_loss_coefficient.py (siehe 03_Documentation/MANUAL.md)
K_WERT = 0.185        # W/K

# Ab welcher Abweichung zwischen Wasser- und Probe-Endtemperatur die
# Gleichgewichtsannahme (Tf = Mittel beider Endwerte) als verletzt gilt.
EQUILIBRIUM_WARN_DELTA = 1.0  # °C

MATERIALS = {
    'Stahl':     {'masse_g': 339},
    'Kupfer':    {'masse_g': 377},
    'Aluminium': {'masse_g': 113}
}

# =========================================================
# DATENSPEICHER
# =========================================================

data_store = {'zeit': [], 'temp_wasser': [], 'temp_wuerfel': []}

# NEU: None statt 0.0, damit "noch kein gueltiger Wert erhalten" von
# "Wert ist 0.0 Grad" unterscheidbar ist.
latest_values = {'t_water': None, 't_sample': None}

# NEU: Zeitpunkt der letzten gueltigen Aktualisierung pro Sensor.
last_update = {'t_water': 0.0, 't_sample': 0.0}

# NEU: Wert, den euer Arduino-Sketch bei nicht angeschlossenem Sensor sendet.
# -127.0 ist der Standard-Fehlerwert der DallasTemperature/DS18B20-Bibliothek.
# Falls euer Sketch stattdessen NaN, -1000 o.ae. sendet: hier anpassen.
SENSOR_ERROR_VALUE = -127.0

# NEU: Nach dieser Zeit ohne gueltigen neuen Wert gilt ein Sensor als
# getrennt, auch wenn kein expliziter Fehlerwert gesendet wird
# (z.B. bei Kabelbruch statt sauberem Abstecken).
SENSOR_TIMEOUT_S = 3.0

experiment_state = {'running': False, 'finished': False}

# Race-Condition-Schutz
data_lock = threading.Lock()

start_time = 0

# =========================================================
# SERIELLE DATEN EINLESEN
# =========================================================

def read_from_arduino():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)

        while True:
            line = ser.readline().decode('utf-8').strip()

            if line:
                try:
                    data = json.loads(line)

                    with data_lock:
                        now = time.time()

                        # NEU: Wasser und Probe unabhaengig voneinander
                        # aktualisieren -- ein fehlender/fehlerhafter Wert
                        # bei einem Sensor blockiert den anderen nicht mehr.
                        tw = data.get('t_water')
                        if tw is not None and tw != SENSOR_ERROR_VALUE:
                            latest_values['t_water'] = tw
                            last_update['t_water'] = now

                        ts = data.get('t_sample')
                        if ts is not None and ts != SENSOR_ERROR_VALUE:
                            latest_values['t_sample'] = ts
                            last_update['t_sample'] = now

                        if experiment_state['running']:
                            elapsed = round(now - start_time, 1)

                            data_store['zeit'].append(elapsed)
                            data_store['temp_wasser'].append(latest_values['t_water'])
                            data_store['temp_wuerfel'].append(latest_values['t_sample'])

                except:
                    pass

    except:
        pass

thread = threading.Thread(target=read_from_arduino, daemon=True)
thread.start()

# =========================================================
# DASH APP
# =========================================================

app = dash.Dash(__name__)

# =========================================================
# LAYOUT
# =========================================================

app.layout = html.Div(
    style={
        'padding': '40px',
        'backgroundColor': '#f4f7f6',
        'fontFamily': 'Segoe UI'
    },
    children=[

        dcc.Download(id='download-csv'),

        html.H1(
            'Wärmekapazitätsversuch',
            style={'textAlign': 'center'}
        ),

        html.Div(
            style={
                'display': 'flex',
                'justifyContent': 'center',
                'gap': '20px',
                'marginBottom': '20px'
            },
            children=[

                html.Div(
                    style={
                        'padding': '15px',
                        'backgroundColor': '#2c3e50',
                        'color': 'white',
                        'borderRadius': '8px',
                        'width': '150px',
                        'textAlign': 'center'
                    },
                    children=[
                        html.H4('Wasser', style={'margin': '0'}),
                        html.Div(
                            id='live-water',
                            style={'fontSize': '28px', 'fontWeight': 'bold'}
                        )
                    ]
                ),

                html.Div(
                    style={
                        'padding': '15px',
                        'backgroundColor': '#c0392b',
                        'color': 'white',
                        'borderRadius': '8px',
                        'width': '150px',
                        'textAlign': 'center'
                    },
                    children=[
                        html.H4('Probe', style={'margin': '0'}),
                        html.Div(
                            id='live-sample',
                            style={'fontSize': '28px', 'fontWeight': 'bold'}
                        )
                    ]
                )
            ]
        ),

        dcc.Graph(id='live-graph', style={'height': '400px'}),

        dcc.Interval(id='graph-update', interval=500),

        html.Div(
            style={
                'padding': '20px',
                'backgroundColor': 'white',
                'borderRadius': '10px',
                'boxShadow': '0 2px 5px rgba(0,0,0,0.1)'
            },
            children=[

                html.H3('Versuchssteuerung'),

                html.Div(
                    style={'display': 'flex', 'gap': '20px', 'marginBottom': '15px', 'alignItems': 'center'},
                    children=[
                        html.Div([
                            html.Label('Wassermasse (g):', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                            dcc.Input(id='input-wasser-masse', type='number', value=300.0, step=1.0, style={'width': '80px'}),
                        ]),
                        html.Div([
                            html.Label('Raumtemperatur (°C):', style={'fontWeight': 'bold', 'marginRight': '10px'}),
                            dcc.Input(id='input-raum-temp', type='number', value=22.0, step=0.1, style={'width': '80px'}),
                        ])
                    ]
                ),

                dcc.Dropdown(
                    id='mat-select',
                    options=[
                        {'label': 'Aluminium (113g)', 'value': 'Aluminium'},
                        {'label': 'Kupfer (377g)', 'value': 'Kupfer'},
                        {'label': 'Stahl (339g)', 'value': 'Stahl'}
                    ],
                    style={'marginBottom': '20px'}
                ),

                html.Div(
                    style={'display': 'flex', 'gap': '10px'},
                    children=[

                        html.Button(
                            'Versuch Starten',
                            id='start-btn',
                            style={
                                'padding': '10px 20px',
                                'fontSize': '16px',
                                'backgroundColor': '#27ae60',
                                'color': 'white',
                                'border': 'none',
                                'borderRadius': '5px',
                                'cursor': 'pointer'
                            }
                        ),

                        html.Button(
                            'Stopp',
                            id='stop-btn',
                            style={
                                'padding': '10px 20px',
                                'fontSize': '16px',
                                'backgroundColor': '#e74c3c',
                                'color': 'white',
                                'border': 'none',
                                'borderRadius': '5px',
                                'cursor': 'pointer'
                            }
                        ),

                        html.Button(
                            'CSV Download',
                            id='download-btn',
                            style={
                                'padding': '10px 20px',
                                'fontSize': '16px',
                                'backgroundColor': '#f39c12',
                                'color': 'white',
                                'border': 'none',
                                'borderRadius': '5px',
                                'cursor': 'pointer'
                            }
                        )
                    ]
                ),

                html.Div(
                    id='status-indicator',
                    style={
                        'marginTop': '20px',
                        'fontSize': '20px',
                        'fontWeight': 'bold'
                    }
                ),

                html.Div(id='calc-output')
            ]
        )
    ]
)

# =========================================================
# HILFSFUNKTIONEN
# =========================================================

def format_temp(key):
    """NEU: zeigt 'Kein Sensor' statt eines eingefrorenen/alten Werts,
    wenn fuer diesen Sensor noch nie ein gueltiger Wert kam oder der
    letzte gueltige Wert laenger als SENSOR_TIMEOUT_S her ist."""
    wert = latest_values[key]
    if wert is None or (time.time() - last_update[key]) > SENSOR_TIMEOUT_S:
        return 'Kein Sensor'
    return f'{wert:.2f} °C'


def mean_last(values, n=5):
    if len(values) < n:
        return sum(values) / len(values)
    return sum(values[-n:]) / n


def _sorted_unique(times, temps):
    """Zeit/Temperatur-Paare nach Zeit sortieren und Duplikate entfernen,
    bevor integriert wird -- ungeordnete oder doppelte Zeitstempel vom
    Arduino wuerden integrate_heat_loss sonst verfaelschen."""
    pairs = sorted(zip(times, temps), key=lambda p: p[0])
    out_t, out_T = [], []
    last_t = None
    for t, T in pairs:
        if last_t is not None and t == last_t:
            continue
        out_t.append(t)
        out_T.append(T)
        last_t = t
    return out_t, out_T


def integrate_heat_loss(times, temps, t_raum):
    '''Integriert den Waermeverlust ueber alle Messpunkte
    (Trapezregel statt linker Rechtecksumme -- etwas genauer bei
    ungleichmaessigen Abtastintervallen).'''

    times, temps = _sorted_unique(times, temps)

    e_loss = 0.0

    for i in range(len(times) - 1):
        dt = times[i + 1] - times[i]
        T_avg = (temps[i] + temps[i + 1]) / 2.0

        # Newtonsche Abkuehlung
        e_loss += K_WERT * (T_avg - t_raum) * dt

    return e_loss


# =========================================================
# CALLBACK
# =========================================================

@app.callback(
    [
        Output('live-water', 'children'),
        Output('live-sample', 'children'),
        Output('live-graph', 'figure'),
        Output('status-indicator', 'children'),
        Output('calc-output', 'children')
    ],
    [
        Input('graph-update', 'n_intervals'),
        Input('start-btn', 'n_clicks'),
        Input('stop-btn', 'n_clicks')
    ],
    [
        State('mat-select', 'value'),
        State('input-wasser-masse', 'value'),
        State('input-raum-temp', 'value')
    ]
)

def update_dashboard(n, start_clicks, stop_clicks, material, wasser_masse, t_raum):

    global start_time

    ctx = dash.callback_context

    # Fallback für leere Eingabefelder
    wasser_masse = float(wasser_masse) if wasser_masse is not None else 300.0
    t_raum = float(t_raum) if t_raum is not None else 22.0

    # =====================================================
    # START / STOP
    # =====================================================

    if ctx.triggered:

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'start-btn' and material:

            experiment_state.update({
                'running': True,
                'finished': False
            })

            with data_lock:
                data_store['zeit'].clear()
                data_store['temp_wasser'].clear()
                data_store['temp_wuerfel'].clear()

            start_time = time.time()

            return (
                format_temp('t_water'),
                format_temp('t_sample'),
                go.Figure(),
                'Status: MESSUNG LÄUFT',
                ''
            )

        elif button_id == 'stop-btn':

            experiment_state['running'] = False
            experiment_state['finished'] = True
        # =====================================================
        # AUTOMATISCHER STOPP
        # =====================================================
        if experiment_state['running'] and len(data_store['zeit']) > 20:
            # NEU: latest_values kann jetzt None sein (Sensor noch nie
            # gueltig empfangen) -- ohne diese Absicherung wuerde die
            # abs()-Differenz weiter unten mit TypeError abstuerzen.
            if (
                latest_values['t_water'] is not None
                and latest_values['t_sample'] is not None
                and abs(latest_values['t_water'] - latest_values['t_sample']) <= 1
            ):
                # Timer initialisieren, falls noch nicht vorhanden
                if 'stability_start' not in experiment_state:
                    experiment_state['stability_start'] = time.time()
                # Stoppen, wenn Wasser und Probe 30 Sekunden lang hoechstens 1 °C auseinanderliegen
                elif time.time() - experiment_state['stability_start'] >= 30:
                    experiment_state['running'] = False
                    experiment_state['finished'] = True
            else:
                # Timer zuruecksetzen, falls Differenz wieder > 1 °C
                experiment_state.pop('stability_start', None)
        # =====================================================
        # ENDE AUTOMATISCHER STOPP
        # =====================================================

    # =====================================================
    # GRAPH
    # =====================================================

    with data_lock:
        zeit = list(data_store['zeit'])
        temp_wasser = list(data_store['temp_wasser'])
        temp_wuerfel = list(data_store['temp_wuerfel'])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=zeit,
            y=temp_wasser,
            name='Wasser',
            line=dict(color='#2c3e50')
        )
    )

    fig.add_trace(
        go.Scatter(
            x=zeit,
            y=temp_wuerfel,
            name='Probe',
            line=dict(color='#c0392b')
        )
    )

    fig.update_layout(
        template='plotly_white',
        xaxis_title='Zeit [s]',
        yaxis_title='Temperatur [°C]',
        margin=dict(l=40, r=40, t=20, b=20)
    )

    # =====================================================
    # BERECHNUNG
    # =====================================================

    result_div = html.Div()

    if (
        experiment_state['finished']
        and material
        and len(zeit) > 15
    ):

        try:

            # -------------------------------------------------
            # STARTWERTE
            # -------------------------------------------------

            t_w_start = sum(temp_wasser[:10]) / 10
            t_e_start = sum(temp_wuerfel[:10]) / 10

            # -------------------------------------------------
            # ENDTEMPERATUREN (gemittelt)
            # -------------------------------------------------

            t_w_end = mean_last(temp_wasser, 5)
            t_e_end = mean_last(temp_wuerfel, 5)

            # -------------------------------------------------
            # GLEICHGEWICHTS-PLAUSIBILITAET
            # -------------------------------------------------
            # Tf = Mittel aus beiden Endwerten ist nur zulaessig, wenn
            # Wasser und Probe am Messende bereits (annaehernd) im
            # Gleichgewicht sind. Sonst verfaelscht die Annahme deltaTw
            # und deltaTe direkt.

            equilibrium_gap = abs(t_w_end - t_e_end)

            # Gemeinsame Endtemperatur
            Tf = (t_w_end + t_e_end) / 2

            # -------------------------------------------------
            # DELTA T
            # -------------------------------------------------

            deltaTw = t_w_start - Tf
            deltaTe = Tf - t_e_start

            # -------------------------------------------------
            # WÄRMEVERLUST INTEGRIEREN
            # -------------------------------------------------

            e_loss = integrate_heat_loss(zeit, temp_wasser, t_raum)

            # -------------------------------------------------
            # ENERGIEBILANZ
            # -------------------------------------------------

            Q_wasser = (
                wasser_masse * 4.182 + C_GEFAESS
            ) * deltaTw

            Q_probe = Q_wasser - e_loss

            # -------------------------------------------------
            # PLAUSIBILITÄT
            # -------------------------------------------------

            if equilibrium_gap > EQUILIBRIUM_WARN_DELTA:

                result_div = html.Div(
                    f'Wasser und Probe liegen am Messende noch '
                    f'{equilibrium_gap:.1f} °C auseinander -- kein '
                    f'Gleichgewicht erreicht. Tf-Annahme (Mittelwert) ist '
                    f'hier nicht gueltig, Ergebnis unzuverlaessig. '
                    f'Versuch laenger laufen lassen.',
                    style={'color': 'red'}
                )

            elif deltaTe <= 0.5:

                result_div = html.Div(
                    'Temperaturanstieg der Probe zu gering.',
                    style={'color': 'orange'}
                )

            elif Q_probe <= 0:

                result_div = html.Div(
                    'Energiebilanz negativ – Versuch zu kurz oder starke Verluste.',
                    style={'color': 'red'}
                )

            else:

                m_cube = MATERIALS[material]['masse_g']

                c_e = Q_probe / (m_cube * deltaTe)

                # Literaturwerte
                literature = {
                    'Aluminium': 0.897,
                    'Kupfer': 0.385,
                    'Stahl': 0.470
                }

                c_lit = literature.get(material, 1.0)

                abweichung = abs(c_e - c_lit) / c_lit * 100

                # Qualitätsbewertung
                if abweichung < 15:
                    bg = '#d4edda'
                    border = '#c3e6cb'
                    qual = 'SEHR GUT'
                elif abweichung < 35:
                    bg = '#fff3cd'
                    border = '#ffeaa7'
                    qual = 'BRAUCHBAR'
                else:
                    bg = '#f8d7da'
                    border = '#f5c6cb'
                    qual = 'GROßE ABWEICHUNG'

                result_div = html.Div(
                    [
                        html.Div(
                            f'c = {c_e:.3f} J/(g·K)',
                            style={
                                'fontSize': '30px',
                                'fontWeight': 'bold',
                                'marginBottom': '10px'
                            }
                        ),

                        html.Div(
                            f'Literatur: {c_lit:.3f} J/(g·K)',
                            style={'fontSize': '18px'}
                        ),

                        html.Div(
                            f'Abweichung: {abweichung:.1f} %',
                            style={'fontSize': '18px'}
                        ),

                        html.Div(
                            f'Wärmeverlust korrigiert: {e_loss:.0f} J',
                            style={'fontSize': '16px', 'marginTop': '8px'}
                        ),

                        html.Div(
                            f'Bewertung: {qual}',
                            style={
                                'fontSize': '18px',
                                'fontWeight': 'bold',
                                'marginTop': '10px'
                            }
                        )
                    ],
                    style={
                        'marginTop': '20px',
                        'padding': '20px',
                        'backgroundColor': bg,
                        'border': f'2px solid {border}',
                        'borderRadius': '8px',
                        'textAlign': 'center'
                    }
                )

        except Exception as e:

            result_div = html.Div(
                f'Berechnungsfehler: {str(e)}',
                style={'color': 'red'}
            )

    # =====================================================
    # STATUS
    # =====================================================

    status = (
        'Status: MESSUNG LÄUFT'
        if experiment_state['running']
        else 'Status: FERTIG'
    )

    return (
        format_temp('t_water'),
        format_temp('t_sample'),
        fig,
        status,
        result_div
    )

# =========================================================
# CSV DOWNLOAD
# =========================================================

@app.callback(
    Output('download-csv', 'data'),
    Input('download-btn', 'n_clicks'),
    prevent_initial_call=True
)

def download_data(n_clicks):

    with data_lock:
        df = pd.DataFrame(data_store)

    return dcc.send_data_frame(
        df.to_csv,
        filename='Messdaten.csv',
        index=False
    )

# =========================================================
# MAIN
# =========================================================

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)