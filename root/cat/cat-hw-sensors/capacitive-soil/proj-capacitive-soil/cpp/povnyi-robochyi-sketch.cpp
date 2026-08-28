// Автополив на ЄМНІСНОМУ щупі v1.2 → Arduino Uno.
// Щуп живиться імпульсно з D7 (економія + чистий замір), AOUT на A0
// читається ковзним середнім, відсотки — за двоточковим калібруванням,
// рішення з гістерезисом, насос через реле на D8. Санітарна перевірка сигналу.

const uint8_t POWER = 7;          // живлення щупа з цифрового виводу
const uint8_t SOIL  = A0;         // AOUT щупа
const uint8_t PUMP  = 8;          // вивід на реле насоса

// калібрування (10-бітний АЦП Uno): зняти для СВОГО щупа.
// ПАМ'ЯТАЙ: велике число = сухо! AIR більше за WATER.
const int AIR   = 610;            // сухо: щуп у повітрі
const int WATER = 330;            // мокро: щуп у воді до межі друку

const int PCT_DRY = 30;           // сухіше за 30 % → вмикаємо полив
const int PCT_WET = 60;           // вологіше за 60 % → вимикаємо
const unsigned long PERIOD = 60000UL;   // міряємо раз на хвилину

bool watering = false;
unsigned long lastMeasure = 0;

// ── ковзне середнє з 16 замірів глушить дрібний шум ──
int readAvg(uint8_t pin, uint8_t n = 16) {
    long sum = 0;
    for (uint8_t i = 0; i < n; i++) { sum += analogRead(pin); delay(2); }
    return (int)(sum / n);        // long у сумі — щоб не переповнити int
}

// ── імпульсне живлення: струм на щуп лише на час заміру ──
int measureRaw() {
    digitalWrite(POWER, HIGH);    // ожив генератор 555
    delay(50);                     // усталення генератора й RC-фільтра щупа
    int v = readAvg(SOIL);
    digitalWrite(POWER, LOW);     // знеструмили — щуп відпочиває
    return v;
}

// ── сире число → відсоток; AIR→0%, WATER→100% (бо велике число = сухо) ──
int toPercent(int raw) {
    int pct = map(raw, AIR, WATER, 0, 100);
    return constrain(pct, 0, 100);
}

// ── груба перевірка «живий сигнал»: ловить мертвий таймер / обрив ──
bool sensorSane(int raw) {
    if (raw <= 2)     return false;   // прилип до нуля
    if (raw >= 1021)  return false;   // прилип до стелі 10-бітного АЦП
    return true;
}

void setup() {
    pinMode(POWER, OUTPUT); digitalWrite(POWER, LOW);
    pinMode(PUMP,  OUTPUT); digitalWrite(PUMP,  LOW);
    Serial.begin(9600);
    Serial.println("автополив (ємнісний щуп) готовий.");
}

void loop() {
    unsigned long now = millis();
    // замір за розкладом — різниця часів переживе переповнення millis()
    if (now - lastMeasure < PERIOD) return;
    lastMeasure = now;

    int raw = measureRaw();

    if (!sensorSane(raw)) {                 // сигнал битий — не поливаємо наосліп
        digitalWrite(PUMP, LOW);
        Serial.print("щуп мовчить (raw="); Serial.print(raw);
        Serial.println("): перевір таймер NE555/TLC555, живлення 3.3В, дроти");
        return;
    }

    int pct = toPercent(raw);

    // рішення з гістерезисом (у відсотках)
    if (!watering && pct < PCT_DRY) watering = true;    // пересохло
    if ( watering && pct > PCT_WET) watering = false;   // напоїлось
    digitalWrite(PUMP, watering ? HIGH : LOW);

    Serial.print("вологість="); Serial.print(pct); Serial.print("%  (raw ");
    Serial.print(raw); Serial.print(")  ");
    Serial.println(watering ? "[полив]" : "[сухо стоїть]");
}
