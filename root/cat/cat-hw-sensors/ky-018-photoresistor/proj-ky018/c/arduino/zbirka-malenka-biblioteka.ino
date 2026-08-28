class LightSensor {
  uint8_t pin;
  int     rawMin, rawMax;     // межі власного діапазону (калібрування)
  float   smoothed;           // згладжена оцінка (EMA)
  float   alpha;              // сила фільтра 0..1
  bool    dark;               // поточний стан (для гістерезису)
  int     onThresh, offThresh;// пороги у ВІДСОТКАХ діапазону

public:
  LightSensor(uint8_t p, float a = 0.2f, int onPct = 30, int offPct = 45)
    : pin(p), rawMin(0), rawMax(0), smoothed(0),
      alpha(a), dark(false), onThresh(onPct), offThresh(offPct) {}

  void begin(int fullScale) {           // fullScale: 1023 для Uno, 4095 для ESP32
    rawMin = fullScale;                 // «перевернуті» старти під пошук min/max
    rawMax = 0;
    smoothed = analogRead(pin);         // засіяти фільтр першим відліком
  }

  // покрутіть освітлення протягом seconds — клас зловить ваші крайнощі
  void calibrate(uint16_t seconds) {
    uint32_t until = millis() + (uint32_t)seconds * 1000;
    while (millis() < until) {
      int v = analogRead(pin);
      if (v < rawMin) rawMin = v;
      if (v > rawMax) rawMax = v;
      delay(5);
    }
    if (rawMax - rawMin < 20) {          // діапазон підозріло вузький — калібрування недійсне
      rawMin = 0; rawMax = 0;            // (нуль-нуль = «не відкалібровано»)
    }
  }

  int  update() {                         // кликати щоцикл: оновлює фільтр, вертає сирий згладжений відлік
    int raw = analogRead(pin);
    smoothed += alpha * (raw - smoothed);
    return (int)smoothed;
  }

  uint8_t percent() {                     // 0..100 % у межах власного діапазону
    if (rawMax <= rawMin) return 0;       // ще не відкалібровано
    int s = (int)smoothed;
    if (s <= rawMin) return 0;
    if (s >= rawMax) return 100;
    return (uint32_t)(s - rawMin) * 100 / (rawMax - rawMin);
  }

  bool isDark() {                         // рішення з гістерезисом, у відсотках
    uint8_t p = percent();
    if (!dark && p < onThresh)       dark = true;    // стало темно
    else if (dark && p > offThresh)  dark = false;   // стало світло
    return dark;
  }
};
