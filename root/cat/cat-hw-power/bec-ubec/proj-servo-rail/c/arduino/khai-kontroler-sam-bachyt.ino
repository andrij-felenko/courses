// ── Монітор просадки UBEC-шини. Arduino (Uno/Nano, ATmega328) ──
// Опорну беремо ВНУТРІШНЮ (1.1 В): міряти власне живлення відносно
// нього самого безглуздо — відношення не зміниться, хоч би шина сіла.
// Дільник під 1.1 В: R1=47к (згори, від шини), R2=10к (до землі):
//   Uвузол = 5.0 · 10/57 = 0.877 В  (нижче за опорну — безпечно)
//   назад:  Uшини = Uвузол · (R1+R2)/R2 = Uвузол · 5.7

const uint8_t  PIN_RAIL = A0;
const float    DIV = (47000.0f + 10000.0f) / 10000.0f;   // = 5.7
const float    VREF_MV = 1100.0f;     // внутрішня опорна ATmega328
const uint16_t BROWNOUT_MV = 4600;    // поріг тривоги, мВ на шині

void setupRailMonitor() {
  analogReference(INTERNAL);          // 1.1 В; перше читання після зміни — викинути
  analogRead(PIN_RAIL);
  Serial.begin(115200);
}

uint16_t readRailMv() {
  uint32_t acc = 0;
  for (uint8_t i = 0; i < 8; i++)     // усереднення 8 вибірок — прибрати шум
    acc += analogRead(PIN_RAIL);      // 0..1023
  float nodeMv = (acc / 8.0f) * VREF_MV / 1023.0f;
  return (uint16_t)(nodeMv * DIV);    // назад у мілівольти шини
}

// Викликати нечасто (напр. раз на 100 мс) з loop() — не блокує.
void serviceRailMonitor() {
  static uint32_t last = 0;
  if (millis() - last < 100) return;
  last = millis();

  uint16_t mv = readRailMv();
  if (mv < BROWNOUT_MV) {
    Serial.print(F("BROWNOUT! шина = ")); Serial.print(mv);
    Serial.println(F(" мВ — рознеси рухи / послаб навантаження"));
    // тут-таки реакція: НЕ починати нову розкладку серв, поки шина не встане,
    // запалити червоний LED, знизити кількість одночасних серв…
  }
}
