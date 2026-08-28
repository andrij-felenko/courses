const uint8_t SOUND = 2;      // вивід OUT давача
const uint8_t LED   = 13;     // вбудований світлодіод плати
unsigned long lastHit = 0;    // час останньої зарахованої події
unsigned long count   = 0;    // лічильник гучних звуків

void setup() {
    pinMode(SOUND, INPUT);    // на платі вже є підтяжка → спокій = 1
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    int level = digitalRead(SOUND);    // 1 = тиша, 0 = гучний звук
    digitalWrite(LED, level == LOW);   // світимо, поки давач бачить звук

    // рахуємо подію, але не частіше ніж раз на 150 мс —
    // інакше один плеск дасть чергу спрацювань
    if (level == LOW && millis() - lastHit > 150) {
        lastHit = millis();
        Serial.print("гучний звук #");
        Serial.println(++count);
    }
    delay(2);   // щільний цикл, щоб не проґавити короткий імпульс
}
