// Реверс полярності на ГОЛІЙ пластині (плата LM358 не задіяна).
// Гребінки пластини — на GPIO25 і GPIO26; між GPIO25 і GPIO34 — опорний
// резистор R_ref, сама пластина — між GPIO34 і GPIO26. Читаємо GPIO34 (ADC1).

const uint8_t DRV_A = 25;           // гребінка A + опорний резистор до NODE
const uint8_t DRV_B = 26;           // гребінка B
const uint8_t NODE  = 34;           // середина подільника → ADC1
const int ADC_FS = 4095;            // повна шкала 12-біт АЦП

const unsigned long PERIOD    = 60000UL; // період між вимірами, мс (тут 1 хв)
const unsigned long SETTLE_MS = 30;      // усталення напруги на подільнику
const int DRY_ENTER = 2600;         // пороги — у нормованих відліках, калібрувати
const int WET_ENTER = 1500;

bool raining = false;
bool flip = false;                  // чергування полярності
unsigned long lastMeasure = 0;

// один вимір: подати полярність, усталити, зчитати середину, знеструмити,
// а тоді нормувати так, щоб «менше = мокріше» незалежно від напрямку струму
int measureOnce(bool reversed) {
    uint8_t hi = reversed ? DRV_B : DRV_A;   // яка гребінка «плюс» цього разу
    uint8_t lo = reversed ? DRV_A : DRV_B;
    pinMode(hi, OUTPUT); digitalWrite(hi, HIGH);
    pinMode(lo, OUTPUT); digitalWrite(lo, LOW);
    delay(SETTLE_MS);                        // коротке усталення напруги на подільнику
    int raw = analogRead(NODE);
    // знеструмлюємо пластину: обидві ноги у Hi-Z, струм крізь вологу спинено
    pinMode(hi, INPUT);
    pinMode(lo, INPUT);
    // при розвороті плечі міняються місцями → відлік інвертується; вирівнюємо
    return reversed ? (ADC_FS - raw) : raw;
}

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);
    pinMode(DRV_A, INPUT);          // старт — пластина знеструмлена (Hi-Z)
    pinMode(DRV_B, INPUT);
}

void loop() {
    if (millis() - lastMeasure >= PERIOD) {
        lastMeasure = millis();
        int v = measureOnce(flip);           // полярність — по черзі
        flip = !flip;

        if (!raining && v < WET_ENTER) raining = true;
        if ( raining && v > DRY_ENTER) raining = false;

        Serial.print("вологість = "); Serial.print(v); Serial.print("  → ");
        Serial.println(raining ? "дощ" : "сухо");
    }
    // весь інший час пластина у Hi-Z, МК вільний (тут доречний і сон)
}
