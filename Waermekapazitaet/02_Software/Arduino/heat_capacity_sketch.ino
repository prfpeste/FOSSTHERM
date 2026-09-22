#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <max6675.h>
#include <math.h>   // fuer isnan()

// --- KONFIGURATION ---
// I2C-Adresse 0x27
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Pins fuer MAX6675 (Probestueck/Sample)
const int thermoDO = 12;
const int thermoCS = 10;
const int thermoCLK = 13;
MAX6675 thermocouple(thermoCLK, thermoCS, thermoDO);

// Pin fuer DS18B20 (Wasser)
#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// Timing fuer 500ms Update-Rate
unsigned long previousMillis = 0;
const long interval = 500;

void setup() {
  Serial.begin(9600);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("System Start...");

  sensors.begin();

  delay(1000);
  lcd.clear();
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // 1. Sensoren auslesen
    sensors.requestTemperatures();
    float tempWater = sensors.getTempCByIndex(0);   // DS18B20
    float tempSample = thermocouple.readCelsius();  // MAX6675

    // NEU: Fehlerfall pro Sensor VOR dem Senden erkennen.
    // DS18B20 meldet Trennung als -127.0 (DEVICE_DISCONNECTED_C) -- eine
    // normale Zahl, kein Problem fuer JSON.
    // MAX6675 meldet einen offenen Thermoelement-Eingang als NaN --
    // Serial.print(NaN) schreibt oft woertlich "nan" ins JSON, was die
    // GANZE Zeile fuer den JSON-Parser ungueltig macht (auch den jeweils
    // anderen, eigentlich intakten Sensor). Deshalb hier abfangen und
    // stattdessen sauberes JSON-"null" senden.
    bool waterOk = (tempWater != DEVICE_DISCONNECTED_C);
    bool sampleOk = !isnan(tempSample);

    // 2. Daten fuer Python via serieller Schnittstelle (JSON)
    Serial.print("{\"t_water\": ");
    if (waterOk) {
      Serial.print(tempWater);
    } else {
      Serial.print("null");
    }
    Serial.print(", \"t_sample\": ");
    if (sampleOk) {
      Serial.print(tempSample);
    } else {
      Serial.print("null");
    }
    Serial.println("}");

    // 3. LCD Display Update
    updateLCD(tempWater, tempSample, waterOk, sampleOk);
  }
}

void updateLCD(float tW, float tS, bool waterOk, bool sampleOk) {
  // Zeile 1: Wasser (DS18B20)
  lcd.setCursor(0, 0);
  lcd.print("Water: ");
  if (waterOk) {
    lcd.print(tW, 1);
    lcd.print(" C  ");
  } else {
    lcd.print("---  C  ");
  }

  // Zeile 2: Probestueck (MAX6675)
  lcd.setCursor(0, 1);
  lcd.print("Sample: ");
  if (sampleOk) {
    lcd.print(tS, 1);
    lcd.print(" C  ");
  } else {
    lcd.print("---  C  ");
  }
}
