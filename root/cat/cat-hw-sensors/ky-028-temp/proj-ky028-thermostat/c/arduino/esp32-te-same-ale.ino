// ESP32: DO на GPIO32 (не strapping), AO на GPIO34 (ADC1, працює з Wi-Fi).
// Живлення KY-028 — від 3V3 ESP32! НЕ від 5V/VIN.
const int DO_PIN = 32;
const int AO_PIN = 34;         // ADC1 — безпечно з увімкненим Wi-Fi
const int LOAD   = 2;          // тут вбудований LED; у бою — керування реле

// 12-бітний АЦП (0..4095): БІЛЬШЕ (після інверсії) = тепліше.
const int WARM_ON  = 2560;     // підібрати під свою намистину
const int WARM_OFF = 2400;     // зазор WARM_OFF..WARM_ON = гістерезис

int  restLevel = HIGH;         // для читання DO як порогу (як на Arduino)
bool state     = false;
int  warmS     = 0;

int readRestLevel() {
    int highs = 0; const int N = 15;
    for (int i = 0; i < N; i++) { if (digitalRead(DO_PIN) == HIGH) highs++; delay(5); }
    return (highs > N / 2) ? HIGH : LOW;
}

void setup() {
    pinMode(DO_PIN, INPUT);    // підтяжка є на модулі
    pinMode(LOAD, OUTPUT);
    Serial.begin(115200);      // на ESP32 звична швидкість вища
    delay(300);
    restLevel = readRestLevel();          // умова: на старті температура в НОРМІ
    warmS = 4095 - analogRead(AO_PIN);    // 12 біт!
    Serial.print("Спокій DO = ");
    Serial.println(restLevel == HIGH ? "HIGH" : "LOW");
}

void loop() {
    // Варіант А: рішення за рівнем AO (поріг задає код) — основний тут.
    int warm = 4095 - analogRead(AO_PIN);          // інверсія на 12 бітах
    warmS += (warm - warmS) / 4;                   // згладжування шуму АЦП

    if (!state && warmS >= WARM_ON) {
        state = true;  digitalWrite(LOAD, HIGH);
        Serial.println(">> ГАРЯЧЕ (AO вище верхнього порогу)");
    } else if (state && warmS <= WARM_OFF) {
        state = false; digitalWrite(LOAD, LOW);
        Serial.println("<< норма (AO нижче нижнього порогу)");
    }

    // Варіант Б (за бажання): паралельно читати апаратний поріг гвинтика.
    // bool hwHot = (digitalRead(DO_PIN) != restLevel);
    // ... можна порівняти з рішенням за рівнем або використати як резерв ...

    delay(50);
}
