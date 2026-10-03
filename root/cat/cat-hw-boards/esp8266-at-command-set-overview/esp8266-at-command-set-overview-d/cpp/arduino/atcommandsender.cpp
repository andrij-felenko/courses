#include <Arduino.h>

// Клас для безпечної генерації та надсилання AT-команд у C++
class AtCommandSender {
private:
    HardwareSerial& serialPort;

public:
    explicit AtCommandSender(HardwareSerial& port) : serialPort(port) {}

    // Надсилання командного рядка з автоматичним термінуванням \r\n
    bool sendCommand(const String& cmd) {
        // Очищення накопичених символів у вхідному буфері Arduino
        while (serialPort.available() > 0) {
            serialPort.read();
        }
        
        // Передача команди та явних символів CRLF
        size_t written = serialPort.print(cmd);
        written += serialPort.print("\r\n");
        
        return written == (cmd.length() + 2);
    }
};
