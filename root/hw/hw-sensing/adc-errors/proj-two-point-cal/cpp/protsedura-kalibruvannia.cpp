#define CAL_PIN 34

Calib cal;

// Зняти N відліків і повернути середнє
int readAvg(int pin, int n = 64) {
    long s = 0;
    for (int i = 0; i < n; i++) s += analogRead(pin);
    return int(s / n);
}

// Інтерактивна сесія калібрування через UART
void runCalibration() {
    Serial.println("=== Калібрування АЦП ===");
    Serial.println("Подайте V_lo (точне джерело, наприклад 0.50 В).");
    Serial.println("Натисніть Enter, коли напруга стабільна:");

    while (!Serial.available()) delay(10);
    Serial.readStringUntil('\n');  // очікуємо Enter
    cal.rawLo = readAvg(CAL_PIN);  // середнє гасить шум
    Serial.printf("raw_lo = %d. Введіть точне значення V_lo (В): ", cal.rawLo);
    cal.vLo = Serial.parseFloat();

    Serial.println("\nПодайте V_hi (наприклад 2.50 В), натисніть Enter:");
    while (!Serial.available()) delay(10);
    Serial.readStringUntil('\n');
    cal.rawHi = readAvg(CAL_PIN);
    Serial.printf("raw_hi = %d. Введіть точне значення V_hi (В): ", cal.rawHi);
    cal.vHi = Serial.parseFloat();

    saveCalib(cal);
    Serial.println("\nКалібрування збережено в NVS.");
}

void setup() {
    Serial.begin(115200);
    analogSetPinAttenuation(CAL_PIN, ADC_11db);  // фіксуємо atten ДО читання

    if (!loadCalib(cal)) {
        Serial.println("[WARN] Калібрування відсутнє. Запустіть runCalibration().");
        // cal лишається {0,0,0,0} — applyCalib поверне fallback
    } else {
        float slope = (cal.vHi - cal.vLo) / float(cal.rawHi - cal.rawLo);
        Serial.printf("[CAL] slope=%.6f V/код, offset_V=%.4f В\n",
                      slope, cal.vLo - slope * cal.rawLo);
    }
}

void loop() {
    int   raw = analogRead(CAL_PIN);
    float v   = applyCalib(cal, raw);
    Serial.println(v, 4);
    delay(200);
}
