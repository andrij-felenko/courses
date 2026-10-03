// Ініціалізація та зміна швидкості UART для ESP-AT (C++ / Arduino)
#include <Arduino.h>

void initAndChangeBaud(uint32_t newBaud) {
    // Ініціалізація початкового порту на 115200 бод
    Serial1.begin(115200);
    
    // 1. Відключення відображення команд (ехо)
    Serial1.print("ATE0\r\n");
    delay(50);
    
    // 2. Надсилання команди зміни швидкості у RAM
    Serial1.printf("AT+UART_CUR=%lu,8,1,0,0\r\n", newBaud);
    Serial1.flush(); // Чекаємо повного виходу даних з буфера TX
    delay(20);
    
    // 3. Переініціалізація послідовного порту хоста на нову швидкість
    Serial1.begin(newBaud);
    delay(50);
    
    // 4. Тестова перевірка зв'язку
    Serial1.print("AT\r\n");
}
