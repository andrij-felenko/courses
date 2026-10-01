#include <Arduino.h>

void setup() {
    // Зчитування структури причини скидання в середовищі Arduino
    rst_info *rst = ESP.getResetInfoPtr();
    
    if (rst->reason == REASON_EXT_SYS_RST) {
        // Обробка зовнішнього апаратного скидання на лінії RST
    }
    
    // Перенаправлення портів UART0 для усунення завад на лініях
    Serial.swap();
}

void loop() {
}
