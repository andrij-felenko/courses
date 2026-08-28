const uint8_t SOUND = 2;                 // вивід DO давача
uint8_t prev = HIGH;                     // попередній рівень (спокій = HIGH)

void setup() {
    pinMode(SOUND, INPUT);               // підтяжка на платі → спокій = 1
    Serial.begin(9600);
}

void loop() {
    uint8_t now = digitalRead(SOUND);
    if (prev == HIGH && now == LOW) {    // спіймали спадний фронт «1→0»
        Serial.println("звук!");
    }
    prev = now;
    // жодних delay: цикл летить, проміжок між читаннями — мікросекунди
}
