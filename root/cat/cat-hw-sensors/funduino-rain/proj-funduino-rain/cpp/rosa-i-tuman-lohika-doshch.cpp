// Відсів роси/туману: «дощ» лише коли мокро БЕЗПЕРЕРВНО довше за N хвилин.
// DO давача на D2 (класична полярність: 0 = мокро, 1 = сухо).

const uint8_t RAIN = 2;
const unsigned long RAIN_MIN_MS = 3UL * 60UL * 1000UL;  // 3 хвилини стійкої вологи
const unsigned long DRY_CLEAR_MS = 30UL * 1000UL;       // 30 с сухо → скидаємо

bool wet = false;                   // миттєво мокро (сира ознака)
bool declaredRain = false;          // ПІДТВЕРДЖЕНИЙ дощ
unsigned long wetSince = 0;         // відколи безперервно мокро
unsigned long drySince = 0;         // відколи безперервно сухо

void setup() {
    pinMode(RAIN, INPUT);
    Serial.begin(9600);
}

void loop() {
    bool nowWet = (digitalRead(RAIN) == LOW);
    unsigned long t = millis();

    if (nowWet) {
        if (!wet) { wet = true; wetSince = t; }   // щойно намокло — засікаємо
        drySince = 0;
        // мокро вже досить довго → це справжній дощ
        if (!declaredRain && t - wetSince >= RAIN_MIN_MS) {
            declaredRain = true;
            Serial.println(">>> ДОЩ підтверджено (мокро > 3 хв)");
        }
    } else {
        if (wet) { wet = false; drySince = t; }   // щойно висохло — засікаємо
        wetSince = 0;
        // сухо вже досить довго → дощ скінчився
        if (declaredRain && t - drySince >= DRY_CLEAR_MS) {
            declaredRain = false;
            Serial.println(">>> сухо, дощ скінчився");
        }
    }
}
