const uint8_t SHOCK = 2;      // вивід S давача
const uint8_t LED   = 13;     // вбудований світлодіод
unsigned long lastHit = 0;    // час останнього зарахованого струсу
unsigned long count   = 0;    // лічильник струсів

void setup() {
    pinMode(SHOCK, INPUT_PULLUP);  // підтяжка вгору: спокій = 1, струс тягне до 0
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    int level = digitalRead(SHOCK);   // 1 = спокій, 0 = контакт замкнувся
    digitalWrite(LED, level == LOW);  // світимо, поки бачимо замикання

    // рахуємо струс, але не частіше ніж раз на 200 мс — гасимо торохтіння пружини
    if (level == LOW && millis() - lastHit > 200) {
        lastHit = millis();
        Serial.print("струс #");
        Serial.println(++count);
    }
    delay(5);   // щільний цикл, щоб не проґавити короткий контакт
}
