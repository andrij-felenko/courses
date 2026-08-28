struct CalPoint { int raw; int level; };

class WaterLevel {
  uint8_t pinPower, pinSignal, pinPump;
  const CalPoint* cal;        // таблиця калібрування (за зростанням raw)
  uint8_t calN;
  int  levelOn, levelOff;     // пороги помпи (у РІВНІ, не в сирих одиницях)
  bool pumpOn;                // поточний стан помпи (для гістерезису)
  uint16_t settleMs;          // пауза усталення після подачі живлення
  uint8_t  samples;           // скільки вибірок усереднювати

public:
  WaterLevel(uint8_t pPower, uint8_t pSignal, uint8_t pPump,
             const CalPoint* table, uint8_t n,
             int onLevel, int offLevel,
             uint8_t nSamples = 8, uint16_t settle = 10)
    : pinPower(pPower), pinSignal(pSignal), pinPump(pPump),
      cal(table), calN(n), levelOn(onLevel), levelOff(offLevel),
      pumpOn(false), settleMs(settle), samples(nSamples) {}

  void begin() {
    pinMode(pinPower, OUTPUT);
    digitalWrite(pinPower, LOW);   // давач знеструмлений
    pinMode(pinPump, OUTPUT);
    digitalWrite(pinPump, LOW);    // помпа вимкнена
  }

  // Один вимір: живимо гребінку лише на цей сеанс, усереднюємо, знеструмлюємо.
  int readRaw() {
    digitalWrite(pinPower, HIGH);
    delay(settleMs);
    long sum = 0;
    for (uint8_t i = 0; i < samples; i++) {
      sum += analogRead(pinSignal);
      delay(2);
    }
    digitalWrite(pinPower, LOW);
    return (int)(sum / samples);
  }

  // Сирий відлік → рівень через багатоточкову таблицю (ламана інтерполяція).
  int toLevel(int raw) {
    if (raw <= cal[0].raw)         return cal[0].level;
    if (raw >= cal[calN - 1].raw)  return cal[calN - 1].level;
    for (uint8_t i = 0; i < calN - 1; i++) {
      if (raw >= cal[i].raw && raw <= cal[i + 1].raw) {
        long span = cal[i + 1].raw - cal[i].raw;
        return cal[i].level + (long)(raw - cal[i].raw)
                              * (cal[i + 1].level - cal[i].level) / span;
      }
    }
    return cal[calN - 1].level;
  }

  // Повний цикл: зміряти, перекласти в рівень, оновити помпу з гістерезисом.
  int update() {
    int level = toLevel(readRaw());
    if (!pumpOn && level > levelOn)       pumpOn = true;
    else if (pumpOn && level < levelOff)  pumpOn = false;
    digitalWrite(pinPump, pumpOn ? HIGH : LOW);
    return level;
  }

  bool isPumpOn() const { return pumpOn; }
};
