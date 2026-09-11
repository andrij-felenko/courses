// Конфігурація апаратних виводів
const uint8_t PIN_PWM = 9;            // Вихід ШІМ для регулювання швидкості
const uint8_t PIN_DIR1 = 7;           // Сигнали напрямку обертання для H-моста
const uint8_t PIN_DIR2 = 8;
const uint8_t PIN_CURRENT_SENSE = A0; // Аналоговий вхід для вимірювання напруги шунта

// Параметри вимірювального кола та струмового захисту
const float SHUNT_RESISTANCE = 0.1f;        // Опір струмовимірювального шунта (Ом)
const float ADC_VREF = 5.0f;                // Опорна напруга АЦП (В)
const int ADC_MAX_VALUE = 1023;             // Роздільна здатність 10-бітного АЦП
const float CURRENT_LIMIT_AMPS = 1.2f;      // Поріг аварійного струму (80% струму зупинки)
const unsigned long STALL_TIMEOUT_MS = 150; // Допустимий час блокування вала (мс)

// Стан драйвера приводу
enum DriverState {
  STATE_STOPPED,
  STATE_RUNNING,
  STATE_FAULT_STALL
};

DriverState driverState = STATE_STOPPED;
unsigned long overcurrentStartTime = 0;
bool isOvercurrentActive = false;

// Аварійне знеструмлення двигуна та переведення моста у вільний вибіг
void emergencyStop() {
  analogWrite(PIN_PWM, 0);
  digitalWrite(PIN_DIR1, LOW);
  digitalWrite(PIN_DIR2, LOW);
  driverState = STATE_FAULT_STALL;
}

// Зчитування та перерахунок напруги шунта в реальний струм якірного кола
float getMotorCurrent() {
  int rawAdc = analogRead(PIN_CURRENT_SENSE);
  float voltage = (rawAdc * ADC_VREF) / ADC_MAX_VALUE;
  return voltage / SHUNT_RESISTANCE;
}

// Запуск мотора з визначеною швидкістю та напрямком
void setMotorSpeed(int speedPwm, bool forward) {
  if (driverState == STATE_FAULT_STALL) {
    return; // Захист блокує запуск до скидання аварійного стану
  }
  digitalWrite(PIN_DIR1, forward ? HIGH : LOW);
  digitalWrite(PIN_DIR2, forward ? LOW : HIGH);
  analogWrite(PIN_PWM, constrain(speedPwm, 0, 255));
  driverState = STATE_RUNNING;
}

// Неблокуючий моніторинг перевантаження за струмом
void processCurrentProtection() {
  if (driverState != STATE_RUNNING) {
    return;
  }

  float current = getMotorCurrent();

  if (current >= CURRENT_LIMIT_AMPS) {
    if (!isOvercurrentActive) {
      // Фіксуємо момент перевищення порогу струму
      isOvercurrentActive = true;
      overcurrentStartTime = millis();
    } else if (millis() - overcurrentStartTime >= STALL_TIMEOUT_MS) {
      // Струм блокування утримується довше критичного таймауту
      emergencyStop();
    }
  } else {
    // Струм упав нижче порогу: завершився пусковий розгін
    isOvercurrentActive = false;
  }
}

void setup() {
  pinMode(PIN_PWM, OUTPUT);
  pinMode(PIN_DIR1, OUTPUT);
  pinMode(PIN_DIR2, OUTPUT);
  pinMode(PIN_CURRENT_SENSE, INPUT);
  emergencyStop();
}

void loop() {
  processCurrentProtection();
}
