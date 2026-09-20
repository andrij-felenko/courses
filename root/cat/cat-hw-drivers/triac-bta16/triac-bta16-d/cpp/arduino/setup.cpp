// Керування оптосимістором BTA16-600B через цифровий вихід Arduino
const int TRIAC_GATE_PIN = 3;

void setup() {
    pinMode(TRIAC_GATE_PIN, OUTPUT);
    digitalWrite(TRIAC_GATE_PIN, LOW); // Навантаження вимкнено
}

void loop() {
    // Увімкнення навантаження 230 В
    digitalWrite(TRIAC_GATE_PIN, HIGH);
    delay(5000);
    
    // Вимкнення навантаження 230 В
    digitalWrite(TRIAC_GATE_PIN, LOW);
    delay(5000);
}
