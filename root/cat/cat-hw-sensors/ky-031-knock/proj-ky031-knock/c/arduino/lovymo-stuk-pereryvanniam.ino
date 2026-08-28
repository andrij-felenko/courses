const uint8_t KNOCK = 2;              // вивід S — на D2 (переривання INT0)
const uint8_t LED   = 13;             // вбудований світлодіод
const unsigned long LOCKOUT = 60;     // глухе вікно після стуку, мс

volatile bool knockFlag = false;      // ставить обробник, скидає loop
unsigned long lastKnock = 0;          // час зарахованого стуку (міряємо в loop)
unsigned long count     = 0;

void onKnock() {                      // обробник: мусить бути КРИХІТНИЙ
    knockFlag = true;                 // єдина дія — звести прапорець
}

void setup() {
    pinMode(KNOCK, INPUT_PULLUP);     // спокій = 1, удар тягне до 0
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
    // ловимо фронт спаду 1→0; digitalPinToInterrupt переводить № піна у № переривання
    attachInterrupt(digitalPinToInterrupt(KNOCK), onKnock, FALLING);
}

void loop() {
    if (knockFlag) {                  // обробник щось зафіксував
        knockFlag = false;            // одразу скидаємо, щоб не зациклитись
        unsigned long now = millis();
        if (now - lastKnock > LOCKOUT) {   // поза глухим вікном — це правдивий стук
            lastKnock = now;
            count++;
            digitalWrite(LED, HIGH);
            Serial.print("стук #");
            Serial.println(count);
        }
        // якщо всередині вікна — прапорець просто з'їдено, це відскок пружини
    }
    if (millis() - lastKnock > 30) digitalWrite(LED, LOW);  // гасимо світлодіод
}
