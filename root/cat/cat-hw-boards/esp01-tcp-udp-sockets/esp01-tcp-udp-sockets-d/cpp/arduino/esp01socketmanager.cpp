#include <Arduino.h>

class ESP01SocketManager {
public:
    // Безпечне виконання циклу сокета з гарантованим вивільненням ресурсів
    bool executeSocketTransaction(uint8_t linkId, String host, uint16_t port, String payload) {
        String startCmd = "AT+CIPSTART=" + String(linkId) + ",\"TCP\",\"" + host + "\"," + String(port);
        
        // Ініціалізація з'єднання
        Serial.println(startCmd);
        if (!waitForResponse("OK", 4000)) {
            closeSocket(linkId);
            return false;
        }

        // Запит на відправку
        String sendCmd = "AT+CIPSEND=" + String(linkId) + "," + String(payload.length());
        Serial.println(sendCmd);
        if (!waitForResponse(">", 2000)) {
            closeSocket(linkId);
            return false;
        }

        // Відправка корисних даних
        Serial.print(payload);
        if (!waitForResponse("SEND OK", 3000)) {
            closeSocket(linkId);
            return false;
        }

        // Закриття сокета після успішного обміну
        closeSocket(linkId);
        return true;
    }

private:
    void closeSocket(uint8_t linkId) {
        Serial.println("AT+CIPCLOSE=" + String(linkId));
        waitForResponse("OK", 1000);
    }

    bool waitForResponse(String expected, uint32_t timeoutMs) {
        uint32_t start = millis();
        while (millis() - start < timeoutMs) {
            if (Serial.find((char*)expected.c_str())) {
                return true;
            }
        }
        return false;
    }
};
