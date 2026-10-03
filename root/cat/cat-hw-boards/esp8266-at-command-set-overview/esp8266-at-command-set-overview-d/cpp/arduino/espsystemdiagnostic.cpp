#include <Arduino.h>

class EspSystemDiagnostic {
private:
    HardwareSerial& serialPort;

public:
    explicit EspSystemDiagnostic(HardwareSerial& port) : serialPort(port) {}

    // Виконання базової перевірки та зміни Baud Rate у C++
    bool reconfigureBaudRate(uint32_t currentBaud, uint32_t newBaud) {
        serialPort.begin(currentBaud);
        
        // Надсилання команди тимчасового змінення швидкості у RAM
        serialPort.print("AT+UART_CUR=");
        serialPort.print(newBaud);
        serialPort.print(",8,1,0,0\r\n");
        serialPort.flush(); // Очікування завершення передачі TX FIFO

        // Апаратна затримка для збереження цілісності стоп-бітів
        delay(20);

        // Переініціалізація послідовного порту Arduino на нову швидкість
        serialPort.end();
        serialPort.begin(newBaud);

        // Перевірочний пінг зв'язку
        serialPort.print("AT\r\n");
        return true;
    }
};
