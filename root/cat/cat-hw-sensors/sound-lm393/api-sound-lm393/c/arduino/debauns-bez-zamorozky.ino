const uint8_t SOUND = 2;
const unsigned long WINDOW = 150;        // вікно дебаунсу, мс
unsigned long lastHit = 0;               // час останньої ЗАРАХОВАНОЇ події
unsigned long count   = 0;
uint8_t prev = HIGH;

void setup() {
    pinMode(SOUND, INPUT);
    Serial.begin(9600);
}

void loop() {
    uint8_t now = digitalRead(SOUND);
    unsigned long t = millis();

    // спадний фронт І минуло вікно від попередньої події
    if (prev == HIGH && now == LOW && t - lastHit > WINDOW) {
        lastHit = t;
        Serial.print("плеск #");
        Serial.println(++count);
    }
    prev = now;
    // програма НЕ спить: тут можна робити будь-що інше
}
