const uint8_t DO_PIN = 2;      // цифровий вихід модуля (поріг)
const uint8_t LED    = 13;     // вбудований світлодіод плати
bool wasHot = false;           // попередній стан, щоб ловити саме ПЕРЕХІД

void setup() {
    pinMode(DO_PIN, INPUT);    // DO вже підтягнутий на платі (відкритий колектор)
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    // на типовій платі: спокій = HIGH, перетин порогу тягне DO в LOW.
    // ЯКЩО твоя партія навпаки — заміни LOW на HIGH у цьому рядку:
    bool hot = (digitalRead(DO_PIN) == LOW);

    digitalWrite(LED, hot ? HIGH : LOW);   // світимо, поки «гаряче»

    if (hot != wasHot) {                   // друкуємо тільки момент перемикання
        Serial.println(hot ? "перетнуло поріг: ГАРЯЧЕ" : "нижче порогу: норма");
        wasHot = hot;
    }
    delay(20);
}
