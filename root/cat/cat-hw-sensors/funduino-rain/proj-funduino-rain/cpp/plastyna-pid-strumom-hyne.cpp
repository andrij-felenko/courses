// Давач дощу цілим модулем: імпульсно живимо VCC модуля з GPIO,
// читаємо AO з ADC1 лише під час короткого вікна. БЕЗ реверсу полярності —
// перевертати живлення плати з LM358 не можна.

const uint8_t PWR = 26;             // живлення VCC модуля (нога GPIO або ключ на транзисторі)
const uint8_t AO  = 34;             // аналоговий вихід модуля → ADC1

const unsigned long PERIOD    = 60000UL; // період між вимірами, мс (тут 1 хв)
const unsigned long SETTLE_MS = 30;      // усталення LM358 + подільника
const int DRY_ENTER_MV = 2400;
const int WET_ENTER_MV = 1500;

bool raining = false;
unsigned long lastMeasure = 0;

// один вимір: подати живлення на весь модуль, усталити, зчитати AO, зняти живлення
int measureOnce() {
    digitalWrite(PWR, HIGH);            // подали живлення на весь модуль
    delay(SETTLE_MS);                   // LM358 і подільник усталюються
    int mv = analogReadMilliVolts(AO);
    digitalWrite(PWR, LOW);             // зняли живлення — струму крізь вологу нема
    return mv;
}

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);
    pinMode(PWR, OUTPUT);
    digitalWrite(PWR, LOW);             // старт — модуль знеструмлений
}

void loop() {
    if (millis() - lastMeasure >= PERIOD) {
        lastMeasure = millis();
        int mv = measureOnce();

        if (!raining && mv < WET_ENTER_MV) raining = true;
        if ( raining && mv > DRY_ENTER_MV) raining = false;

        Serial.print("AO = "); Serial.print(mv); Serial.print(" мВ  → ");
        Serial.println(raining ? "дощ" : "сухо");
    }
    // весь інший час модуль знеструмлений, МК вільний (тут доречний і сон)
}
