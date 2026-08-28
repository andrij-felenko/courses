const uint8_t RAIN = 4;             // DO на GPIO4
const uint8_t LED  = 2;             // вбудований світлодіод (на більшості плат GPIO2)
const unsigned long SETTLE = 400;

bool raining = false, candidate = false;
unsigned long changedAt = 0;

void setup() {
    pinMode(RAIN, INPUT);
    pinMode(LED, OUTPUT);
    Serial.begin(115200);
}

void loop() {
    bool now = (digitalRead(RAIN) == LOW);
    if (now != candidate) { candidate = now; changedAt = millis(); }
    if (candidate != raining && millis() - changedAt > SETTLE) {
        raining = candidate;
        digitalWrite(LED, raining);
        Serial.println(raining ? "дощ почався" : "дощ скінчився");
    }
}
