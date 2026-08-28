#include <NewPing.h>

const uint8_t SONAR_NUM = 3;
const unsigned int MAX_DISTANCE = 300;

NewPing sonar[SONAR_NUM] = {          // {TRIG, ECHO, макс. відстань}
    NewPing(4, 5,  MAX_DISTANCE),     // ліворуч
    NewPing(6, 7,  MAX_DISTANCE),     // прямо
    NewPing(8, 9,  MAX_DISTANCE)      // праворуч
};

void loop() {
    for (uint8_t i = 0; i < SONAR_NUM; i++) {
        delay(35);                    // пауза між СУСІДНІМИ пострілами
        unsigned int cm = sonar[i].ping_cm();
        Serial.print(cm == 0 ? 999 : cm);
        Serial.print('\t');
    }
    Serial.println();
}
