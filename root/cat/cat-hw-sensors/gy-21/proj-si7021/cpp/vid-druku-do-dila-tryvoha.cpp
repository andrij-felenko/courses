#include <Wire.h>
#include <Adafruit_Si7021.h>

Adafruit_Si7021 sensor;

const int   ALARM_LED = 13;     // вбудований світлодіод як індикатор тривоги
const float RH_ON  = 70.0;      // увімкнути тривогу на цій вологості
const float RH_OFF = 65.0;      // вимкнути — лише коли впаде до цієї

bool alarm = false;             // поточний стан тривоги (пам'ять гістерезису)

void setup() {
  Serial.begin(115200);
  pinMode(ALARM_LED, OUTPUT);
  Wire.begin();                 // на ESP32 — Wire.begin(21, 22)
  if (!sensor.begin()) {
    Serial.println(F("GY-21 не відповідає. Перевірте дроти."));
    while (true) { delay(1000); }
  }
}

void loop() {
  float t  = sensor.readTemperature();
  float rh = sensor.readHumidity();

  // -- гістерезис: перемикаємо стан лише на перетині відповідної межі --
  if (!alarm && rh >= RH_ON) {
    alarm = true;
    digitalWrite(ALARM_LED, HIGH);
    Serial.println(F("!! ТРИВОГА: вологість вища за безпечну"));
  } else if (alarm && rh <= RH_OFF) {
    alarm = false;
    digitalWrite(ALARM_LED, LOW);
    Serial.println(F("-- вологість повернулась у норму"));
  }

  Serial.print(F("T = "));       Serial.print(t, 1);
  Serial.print(F(" °C  RH = "));  Serial.print(rh, 1);
  Serial.println(alarm ? F(" %  [тривога]") : F(" %"));

  delay(2000);                  // раз на 2 с — і давач не гріє себе
}
