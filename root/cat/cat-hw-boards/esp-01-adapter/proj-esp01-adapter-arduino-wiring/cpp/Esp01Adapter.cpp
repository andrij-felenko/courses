#include "Esp01Adapter.hpp"

// Конструктор: зберігає піни та ініціалізує об'єкт SoftwareSerial
Esp01Adapter::Esp01Adapter(uint8_t rxPin, uint8_t txPin)
    : m_rxPin(rxPin), m_txPin(txPin), m_espSerial(rxPin, txPin) {
}

// Деструктор: зупиняє програмний порт
Esp01Adapter::~Esp01Adapter() {
    m_espSerial.end();
}

// Запуск програмного порту з затримкою для стабілізації
void Esp01Adapter::begin(unsigned long baud) {
    m_espSerial.begin(baud);
    delay(100);
}

// Двостороння ретрансляція даних між ПК (Serial) та ESP-01 (m_espSerial)
void Esp01Adapter::processBridge() {
    // Пересилання байтів від Serial Monitor (ПК) до модуля ESP-01
    while (Serial.available() > 0) {
        char inChar = static_cast<char>(Serial.read());
        m_espSerial.write(inChar);
    }

    // Пересилання байтів від модуля ESP-01 до Serial Monitor (ПК)
    while (m_espSerial.available() > 0) {
        char inChar = static_cast<char>(m_espSerial.read());
        Serial.write(inChar);
    }
}

// Відправка AT-команди з очікуванням відповіді
String Esp01Adapter::sendCommand(const String& command, unsigned int timeoutMs) {
    String response = "";

    // Очищення вхідного буфера перед відправкою
    while (m_espSerial.available() > 0) {
        m_espSerial.read();
    }

    // Надсилання команди з поверненням каретки та переведенням рядка
    m_espSerial.println(command);

    unsigned long startTime = millis();
    while (millis() - startTime < timeoutMs) {
        while (m_espSerial.available() > 0) {
            char c = static_cast<char>(m_espSerial.read());
            response += c;
        }
        delay(2);
    }

    return response;
}

// Виконання сканування точок доступу Wi-Fi (AT+CWLAP)
void Esp01Adapter::scanNetworks() {
    Serial.println(F("[ESP01] Переведення модуля в режим Station (AT+CWMODE=1)..."));
    sendCommand("AT+CWMODE=1", 1000);

    Serial.println(F("[ESP01] Запуск сканування Wi-Fi мереж (AT+CWLAP)..."));
    String response = sendCommand("AT+CWLAP", 6000);

    if (response.length() == 0) {
        Serial.println(F("[ESP01] Помилка: модуль не надав відповіді. Перевірте підключення та живлення."));
        return;
    }

    Serial.println(F("=================================================="));
    Serial.println(F("           ЗНАЙДЕНІ WI-FI МЕРЕЖІ                "));
    Serial.println(F("=================================================="));
    Serial.println(F("№   | Тип шифрування  | SSID                 | RSSI (дБм)"));
    Serial.println(F("----+-----------------+----------------------+-----------"));

    int apCount = 0;
    int startIndex = 0;

    // Розбір відповіді рядок за рядком
    while (startIndex < response.length()) {
        int endIndex = response.indexOf('\n', startIndex);
        if (endIndex == -1) {
            endIndex = response.length();
        }

        String line = response.substring(startIndex, endIndex);
        line.trim();

        if (line.startsWith("+CWLAP:")) {
            apCount++;
            Serial.print(apCount);
            if (apCount < 10) {
                Serial.print(F("   | "));
            } else {
                Serial.print(F("  | "));
            }

            parseAndPrintAP(line);
        }

        startIndex = endIndex + 1;
    }

    if (apCount == 0) {
        Serial.println(F("Мереж не знайдено або отримати список не вдалося."));
        Serial.println(F("Отримана відповідь:"));
        Serial.println(response);
    }

    Serial.println(F("=================================================="));
}

// Парсинг та форматований вивід параметрів точки доступу
void Esp01Adapter::parseAndPrintAP(const String& line) {
    int firstOpenParen = line.indexOf('(');
    int lastCloseParen = line.lastIndexOf(')');

    if (firstOpenParen == -1 || lastCloseParen == -1 || lastCloseParen <= firstOpenParen) {
        Serial.println(line);
        return;
    }

    String content = line.substring(firstOpenParen + 1, lastCloseParen);

    int firstComma = content.indexOf(',');
    int firstQuote = content.indexOf('"');
    int secondQuote = content.indexOf('"', firstQuote + 1);
    int thirdComma = content.indexOf(',', secondQuote + 1);
    int fourthComma = content.indexOf(',', thirdComma + 1);

    String ecnStr = content.substring(0, firstComma);
    String ssidStr = content.substring(firstQuote + 1, secondQuote);
    String rssiStr = "";

    if (thirdComma != -1) {
        if (fourthComma != -1) {
            rssiStr = content.substring(thirdComma + 1, fourthComma);
        } else {
            rssiStr = content.substring(thirdComma + 1);
        }
    }
    rssiStr.trim();

    int ecn = ecnStr.toInt();
    String encType = "";
    switch (ecn) {
        case 0: encType = "Open           "; break;
        case 1: encType = "WEP            "; break;
        case 2: encType = "WPA_PSK        "; break;
        case 3: encType = "WPA2_PSK       "; break;
        case 4: encType = "WPA_WPA2_PSK   "; break;
        default: encType = "Unknown        "; break;
    }

    Serial.print(encType);
    Serial.print(F(" | "));

    Serial.print(ssidStr);
    for (int i = ssidStr.length(); i < 20; i++) {
        Serial.print(' ');
    }
    Serial.print(F(" | "));
    Serial.println(rssiStr);
}
