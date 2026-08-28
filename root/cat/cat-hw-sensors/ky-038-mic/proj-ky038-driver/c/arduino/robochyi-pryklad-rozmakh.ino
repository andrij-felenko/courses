const uint8_t PIN_AO = A0;
const uint16_t WINDOW_MS = 50;         // тривалість вікна вимірювання
const int ADC_MAX = 1023;              // стеля 10-бітного АЦП ATmega328

int  center  = 512;                     // де стоїть центр сигналу (для контролю країв)
bool clipped = false;                   // чи вперся сигнал у край АЦП цього вікна

// Одне вимірювання: розмах за вікно + перевірка, чи сигнал не б'ється об краї.
int measureAmplitude() {
    int lo = ADC_MAX, hi = 0;
    unsigned long t0 = millis();
    while (millis() - t0 < WINDOW_MS) {
        int v = analogRead(PIN_AO);
        if (v > hi) hi = v;
        if (v < lo) lo = v;
    }
    center  = (hi + lo) / 2;                     // центр вікна = де сидить зсув
    clipped = (hi >= ADC_MAX) || (lo <= 0);      // уперлися в стелю чи підлогу?
    return hi - lo;                              // розмах = груба гучність
}

// Перевести розмах у грубі рівні (пороги підбери під свій модуль і гвинтик).
const char* loudnessLevel(int amp) {
    if (amp < 8)   return "тиша";
    if (amp < 30)  return "чутно";
    if (amp < 120) return "голосно";
    return "дуже голосно";
}

void setup() {
    pinMode(PIN_AO, INPUT);
    Serial.begin(9600);
    delay(300);                        // дати мікрофону встановити зсув після ввімкнення
}

void loop() {
    int amp = measureAmplitude();
    Serial.print("розмах = ");
    Serial.print(amp);
    Serial.print("  →  ");
    Serial.print(loudnessLevel(amp));
    if (clipped) {                     // сигнал уперся в край — розмаху не вір
        Serial.print("  [!] обрізання: центр=");
        Serial.print(center);
        Serial.print(", підправ гвинтик до середини");
    }
    Serial.println();
}
