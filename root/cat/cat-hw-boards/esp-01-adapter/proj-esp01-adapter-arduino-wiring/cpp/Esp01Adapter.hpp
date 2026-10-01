#ifndef ESP01_ADAPTER_HPP
#define ESP01_ADAPTER_HPP

#include <Arduino.h>
#include <SoftwareSerial.h>

/**
 * @brief Клас Esp01Adapter інкапсулює роботу з Wi-Fi модулем ESP-01 через адаптер
 * та програмний послідовний порт SoftwareSerial.
 * 
 * Забезпечує ініціалізацію зв'язку, двосторонній міст (ретрансляцію) між ПК та ESP-01,
 * відправку AT-команд, а також виконання сканування Wi-Fi мереж (AT+CWLAP) з парсингом відповідей.
 */
class Esp01Adapter {
public:
    /**
     * @brief Конструктор адаптера ESP-01.
     * @param rxPin Вивід RX Arduino (підключається до TX модуля ESP-01).
     * @param txPin Вивід TX Arduino (підключається до RX модуля ESP-01 через адаптер/дільник).
     */
    Esp01Adapter(uint8_t rxPin = 2, uint8_t txPin = 3);

    /**
     * @brief Деструктор класу для закриття порту.
     */
    ~Esp01Adapter();

    /**
     * @brief Ініціалізація програмного послідовного порту на заданій швидкості.
     * @param baud Швидкість передачі даних для ESP-01 (за замовчуванням 9600 бод).
     */
    void begin(unsigned long baud = 9600);

    /**
     * @brief Двостороння ретрансляція даних між ПК (Hardware Serial) та ESP-01 (SoftwareSerial) у реальному часі.
     * Слід викликати циклічно у loop().
     */
    void processBridge();

    /**
     * @brief Відправка AT-команди на ESP-01 та очікування відповіді із заданим таймаутом.
     * @param command Рядок AT-команди (наприклад, "AT" або "AT+GMR").
     * @param timeoutMs Максимальний час очікування відповіді в мілісекундах.
     * @return String Текст відповіді від модуля.
     */
    String sendCommand(const String& command, unsigned int timeoutMs = 2000);

    /**
     * @brief Виконує AT+CWLAP та виводить відформатований список доступних Wi-Fi мереж у Serial Monitor.
     */
    void scanNetworks();

private:
    uint8_t m_rxPin;
    uint8_t m_txPin;
    SoftwareSerial m_espSerial;

    /**
     * @brief Парсить окремий рядок +CWLAP та виводить інформацію про точку доступу.
     * @param line Рядок у форматі +CWLAP:(ecn,"ssid",rssi,"mac",channel)
     */
    void parseAndPrintAP(const String& line);
};

#endif // ESP01_ADAPTER_HPP
