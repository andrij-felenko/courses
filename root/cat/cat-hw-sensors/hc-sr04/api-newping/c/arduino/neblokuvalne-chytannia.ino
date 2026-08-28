#include <NewPing.h>

const uint8_t TRIG_PIN = 9;
const uint8_t ECHO_PIN = 10;
const unsigned int MAX_DISTANCE = 300;

NewPing sonar(TRIG_PIN, ECHO_PIN, MAX_DISTANCE);

unsigned int lastCm = 0;      // сюди кладемо готовий результат
unsigned long pingTimer = 0;  // коли робити наступний постріл

void echoCheck() {            // бібліотека кличе це багато разів за вимір
    if (sonar.check_timer()) {              // луна повернулась?
        // ping_result — сирий час у мкс; US_ROUNDTRIP_CM — власна константа
        // бібліотеки (=57, тобто її «58» для трохи теплішого повітря).
        lastCm = sonar.ping_result / US_ROUNDTRIP_CM;
    }
}

void setup() {
    Serial.begin(9600);
    pingTimer = millis() + 75;
}

void loop() {
    // Кожні 75 мс — запускаємо новий вимір (сам постріл миттєвий).
    if (millis() >= pingTimer) {
        pingTimer += 75;
        sonar.ping_timer(echoCheck);   // стартуємо й ОДРАЗУ йдемо далі
    }

    // ...тут процесор вільний: крути мотори, читай Bluetooth, блимай...
    // lastCm завжди тримає найсвіжіший вимір, ні на що не чекаючи.
}
