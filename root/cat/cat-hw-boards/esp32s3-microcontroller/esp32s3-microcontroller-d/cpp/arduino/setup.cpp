#include <Arduino.h>

void setup() {
    // Ініціалізація послідовного порту через нативний USB Serial/JTAG (GPIO19/GPIO20)
    Serial.begin(115200);
    
    // Призначення виводу GPIO4 як цифрового виходу
    pinMode(4, OUTPUT);
}

void loop() {
    digitalWrite(4, HIGH);
    delay(500);
    digitalWrite(4, LOW);
    delay(500);
}
