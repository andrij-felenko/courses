// Керування двофазним циклом живлення нагрівача MQ-7 для Arduino
const uint8_t HEATER_PIN = 9;
const uint8_t ANALOG_PIN = A0;

enum HeaterState {
  HEATER_CLEANING_5V,
  HEATER_MEASURING_1V4
};

HeaterState currentState = HEATER_CLEANING_5V;
unsigned long stateStartTime = 0;

void setup() {
  pinMode(HEATER_PIN, OUTPUT);
  Serial.begin(115200);
  stateStartTime = millis();
  // Вмикаємо фазу очищення 5 В (ключ відкритий)
  digitalWrite(HEATER_PIN, HIGH);
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentState == HEATER_CLEANING_5V) {
    if (currentMillis - stateStartTime >= 60000UL) { // 60 секунд
      currentState = HEATER_MEASURING_1V4;
      stateStartTime = currentMillis;
      digitalWrite(HEATER_PIN, LOW); // Перемикаємо на 1.4 В
    }
  } else if (currentState == HEATER_MEASURING_1V4) {
    if (currentMillis - stateStartTime >= 90000UL) { // 90 секунд
      // Знімаємо аналогове значення наприкінці фази вимірювання
      int rawAdc = analogRead(ANALOG_PIN);
      float voltage = (rawAdc * 5.0) / 1023.0;
      Serial.print("V_AOUT = ");
      Serial.println(voltage);

      // Переходимо на новий цикл очищення
      currentState = HEATER_CLEANING_5V;
      stateStartTime = currentMillis;
      digitalWrite(HEATER_PIN, HIGH);
    }
  }
}
