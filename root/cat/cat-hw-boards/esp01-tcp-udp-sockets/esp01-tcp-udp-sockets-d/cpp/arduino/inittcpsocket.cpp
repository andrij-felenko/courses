#include <Arduino.h>

bool initTcpSocket(uint8_t linkId, const String& remoteIp, uint16_t port) {
    // Встановлення режиму мультиплексування сокетів
    Serial.print("AT+CIPMUX=1\r\n");
    if (!Serial.find("OK")) {
        return false;
    }

    // Створення незахищеного TCP з'єднання
    String cmd = "AT+CIPSTART=" + String(linkId) + ",\"TCP\",\"" + remoteIp + "\"," + String(port) + "\r\n";
    Serial.print(cmd);

    // Очікування підтвердження встановлення зв'язку
    if (Serial.find("CONNECT") || Serial.find("OK")) {
        return true;
    }
    return false;
}
