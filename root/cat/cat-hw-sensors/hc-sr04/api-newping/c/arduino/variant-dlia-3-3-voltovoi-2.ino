// ESP32 без бібліотеки. ECHO — через подільник 1к/2к!
const uint8_t TRIG_PIN = 5;
const uint8_t ECHO_PIN = 18;
const unsigned long ECHO_TIMEOUT_US = 40000UL;

void setup() {
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    digitalWrite(TRIG_PIN, LOW);
    Serial.begin(115200);
}

unsigned int measureCm() {
    digitalWrite(TRIG_PIN, LOW);  delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    unsigned long t = pulseIn(ECHO_PIN, HIGH, ECHO_TIMEOUT_US);
    if (t == 0) return 0;
    return (unsigned int)(t / 58);
}

void loop() {
    unsigned int cm = measureCm();
    if (cm == 0) Serial.println("out of range");
    else         Serial.printf("%u cm\n", cm);
    delay(60);
}
