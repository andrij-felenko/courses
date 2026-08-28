// Автополив на резистивному щупі вологості + LM393 → Arduino Uno.
// Щуп живиться ІМПУЛЬСНО з D7 (проти корозії), AO на A0 читається медіаною,
// калібрування у EEPROM, рішення з гістерезисом, насос через реле на D8.

#include <EEPROM.h>

const uint8_t POWER = 7;          // живлення щупа з цифрового виводу
const uint8_t SOIL  = A0;         // AO давача
const uint8_t PUMP  = 8;          // вивід на реле насоса
const uint8_t BTN   = 3;          // кнопка калібрування (друга нога на GND)

const int PCT_DRY = 30;           // сухіше за 30 % → вмикаємо полив
const int PCT_WET = 60;           // вологіше за 60 % → вимикаємо
const unsigned long PERIOD = 60000UL;   // міряємо раз на хвилину

int  rawDry = 730, rawWet = 300;  // краї калібрування (сире число АЦП)
bool watering = false;
unsigned long lastMeasure = 0;

// ── читання: медіана 9 замірів глушить викиди ──
int median9() {
    int a[9];
    for (int i = 0; i < 9; i++) { a[i] = analogRead(SOIL); delay(2); }
    for (int i = 0; i < 8; i++)
        for (int j = 0; j < 8 - i; j++)
            if (a[j] > a[j+1]) { int t=a[j]; a[j]=a[j+1]; a[j+1]=t; }
    return a[4];
}

// ── імпульсне живлення: струм на щуп лише на час заміру ──
int measureRaw() {
    digitalWrite(POWER, HIGH);
    delay(10);
    int v = median9();
    digitalWrite(POWER, LOW);
    return v;
}

// ── калібрування у/з EEPROM ──
void saveCalib() { EEPROM.put(0, rawDry); EEPROM.put(sizeof(rawDry), rawWet); }
void loadCalib() {
    EEPROM.get(0, rawDry);
    EEPROM.get(sizeof(rawDry), rawWet);
    if (rawDry <= rawWet) { rawDry = 730; rawWet = 300; }   // порожня EEPROM → дефолти
}

// ── сире число → відсоток вологості (більше число = сухіше) ──
int toPercent(int raw) {
    if (rawDry <= rawWet) return -1;
    long pct = (long)(rawDry - raw) * 100 / (rawDry - rawWet);
    if (pct < 0) pct = 0; if (pct > 100) pct = 100;
    return (int)pct;
}

void setup() {
    pinMode(POWER, OUTPUT); digitalWrite(POWER, LOW);
    pinMode(PUMP,  OUTPUT); digitalWrite(PUMP,  LOW);
    pinMode(BTN, INPUT_PULLUP);
    Serial.begin(9600);
    loadCalib();
    Serial.println("автополив готовий. пороги у %.");
}

void loop() {
    // калібрування кнопкою: тримаєш при щупі в повітрі → сухий край;
    // короткий тик при щупі у воді → мокрий край (тут спрощено — по натиску)
    if (digitalRead(BTN) == LOW) {
        delay(30);                             // антибрязк кнопки
        if (digitalRead(BTN) == LOW) {
            int r = measureRaw();
            // евристика: велике число (сухо) → це rawDry, мале → rawWet
            if (r > (rawDry + rawWet) / 2) rawDry = r; else rawWet = r;
            saveCalib();
            Serial.print("калібр: rawDry="); Serial.print(rawDry);
            Serial.print("  rawWet=");        Serial.println(rawWet);
            while (digitalRead(BTN) == LOW) ;  // чекаємо відпускання
        }
    }

    // замір за розкладом — не частіше, ніж раз на PERIOD
    unsigned long now = millis();
    if (now - lastMeasure >= PERIOD) {         // різниця часів — переживе переповнення millis()
        lastMeasure = now;
        int raw = measureRaw();
        int pct = toPercent(raw);

        // рішення з гістерезисом (у відсотках)
        if (!watering && pct >= 0 && pct < PCT_DRY) watering = true;   // пересохло
        if ( watering && pct > PCT_WET)             watering = false;  // напоїлось
        digitalWrite(PUMP, watering ? HIGH : LOW);

        Serial.print("вологість="); Serial.print(pct); Serial.print("%  (АЦП ");
        Serial.print(raw); Serial.print(")  ");
        Serial.println(watering ? "[полив]" : "[сухо стоїть]");
    }
}
