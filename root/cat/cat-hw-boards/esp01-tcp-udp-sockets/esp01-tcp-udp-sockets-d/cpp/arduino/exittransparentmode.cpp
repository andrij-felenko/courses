#include <Arduino.h>

bool exitTransparentMode(HardwareSerial &port) {
    // 1. Витримуємо Guard Time до відправки +++
    delay(1050);

    // 2. Надсилаємо рівно три символи + без \r\n
    port.print("+++");
    port.flush();

    // 3. Витримуємо Guard Time після відправки +++
    delay(1050);

    // 4. Відправляємо перевірочну команду AT
    port.print("AT\r\n");
    
    return true;
}
