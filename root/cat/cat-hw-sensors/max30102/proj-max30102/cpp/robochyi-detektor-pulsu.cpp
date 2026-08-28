#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"        // детектор ударів (PBA)

MAX30105 particleSensor;

const byte RATE_SIZE = 4;     // по скількох останніх BPM усереднюємо
byte rates[RATE_SIZE];        // кільцевий буфер значень
byte rateSpot = 0;
long lastBeat = 0;            // час попереднього удару, мс

float beatsPerMinute;
int   beatAvg;

void setup() {
  Serial.begin(115200);
  Serial.println(F("Детектор пульсу — запуск"));

  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println(F("Чип не знайдено. Перевір живлення/дроти."));
    while (1);
  }
  Serial.println(F("Прикладіть палець з рівним, легким натиском."));

  particleSensor.setup();                       // типові налаштування достатні
  particleSensor.setPulseAmplitudeRed(0x0A);    // тьмяний червоний — індикатор «живе»
  particleSensor.setPulseAmplitudeGreen(0);     // зеленого немає — вимикаємо
}

void loop() {
  long irValue = particleSensor.getIR();

  if (checkForBeat(irValue)) {                  // щойно стався удар?
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60000.0 / delta;           // миттєвий пульс

    if (beatsPerMinute < 255 && beatsPerMinute > 20) {   // відсіяти дурню
      rates[rateSpot++] = (byte)beatsPerMinute;
      rateSpot %= RATE_SIZE;                     // рух по кільцю

      beatAvg = 0;                               // середнє по буферу
      for (byte x = 0; x < RATE_SIZE; x++) beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
    }
  }

  Serial.print(F("IR="));      Serial.print(irValue);
  Serial.print(F(" BPM="));    Serial.print(beatsPerMinute);
  Serial.print(F(" AvgBPM=")); Serial.print(beatAvg);
  if (irValue < 50000) Serial.print(F("   — пальця немає?"));
  Serial.println();
}
