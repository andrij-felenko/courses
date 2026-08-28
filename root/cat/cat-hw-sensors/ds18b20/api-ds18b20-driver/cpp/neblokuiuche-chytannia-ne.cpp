#include <OneWire.h>
#include <DallasTemperature.h>

OneWire oneWire(4);
DallasTemperature sensors(&oneWire);

const uint16_t CONV_MS = 750;         // час конверсії на 12 бітах (із запасом)
uint32_t convStartedAt = 0;           // коли востаннє запустили конверсію
bool converting = false;              // чи чекаємо зараз результат

void setup() {
  Serial.begin(115200);
  sensors.begin();
  sensors.setWaitForConversion(false);   // КЛЮЧОВЕ: не блокувати на конверсії
}

void loop() {
  uint32_t now = millis();

  if (!converting) {
    sensors.requestTemperatures();       // старт; повертає ОДРАЗУ, не чекає
    convStartedAt = now;
    converting = true;
  } else if (now - convStartedAt >= CONV_MS) {
    float t = sensors.getTempCByIndex(0);  // час минув — результат готовий
    if (t != DEVICE_DISCONNECTED_C)
      Serial.printf("t = %.2f C\n", t);
    converting = false;                  // цикл замкнувся: наступний старт
  }

  // ↓ Сюди вписуй усе, що має жити безперервно —
  //   воно тепер крутиться ВЕСЬ час конверсії, а не стоїть.
  pollButtons();
  updateDisplay();
  runControlLoop();
}
