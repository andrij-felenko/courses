#include <NewPing.h>

const uint8_t TRIG_PIN = 9;
const uint8_t ECHO_PIN = 10;
const unsigned int MAX_DISTANCE = 300;   // см; далі не цікавить — не чекаємо

NewPing sonar(TRIG_PIN, ECHO_PIN, MAX_DISTANCE);

void setup() {
    Serial.begin(9600);
}

void loop() {
    delay(60);                            // пауза між вимірами ≥ 60 мс
    unsigned int cm = sonar.ping_cm();    // 0 = поза межами / порожньо
    if (cm == 0) Serial.println(F("out of range"));
    else       { Serial.print(cm); Serial.println(F(" cm")); }
}
