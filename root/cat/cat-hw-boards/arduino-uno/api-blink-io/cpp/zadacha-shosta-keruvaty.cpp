const uint8_t PIN_MOTOR = 9;   // база транзистора через резистор ~1 кОм; вивід ~9 → можна ШІМ

void setup() {
    pinMode(PIN_MOTOR, OUTPUT);
}

void loop() {
    analogWrite(PIN_MOTOR, 180);   // ~70% обертів (ШІМ керує швидкістю)
    delay(2000);
    analogWrite(PIN_MOTOR, 0);     // стоп
    delay(1000);
}
