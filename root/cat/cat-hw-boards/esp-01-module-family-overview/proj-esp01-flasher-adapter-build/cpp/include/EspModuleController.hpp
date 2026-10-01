#ifndef ESP_MODULE_CONTROLLER_HPP
#define ESP_MODULE_CONTROLLER_HPP

#include <Arduino.h>

/**
 * @brief Ревізії модулів сімейства ESP8266 ESP-01.
 */
enum class ModuleRevision {
    Esp01,  ///< Класичний ESP-01 (світлодіод на GPIO1/TX, відсутні внутрішні підтяжки)
    Esp01S  ///< Оновлений ESP-01S (світлодіод на GPIO2, вбудовані резистори підтяжки)
};

/**
 * @brief Конфігурація послідовного порту UART.
 */
struct UartConfig {
    unsigned long baudRate{115200}; ///< Швидкість передачі даних у бодах
};

/**
 * @brief Конфігурація керування світлодіодом.
 */
struct LedConfig {
    uint8_t gpioPin;      ///< Номер виводу GPIO, до якого підключено світлодіод
    bool activeLow{true}; ///< Прапорець інвертованого логічного рівня (true: 0 = УВІМК, 1 = ВИМК)
};

/**
 * @brief Клас для апаратно-програмного керування модулями ESP-01 та ESP-01S.
 * 
 * Забезпечує ініціалізацію UART, керування вбудованим світлодіодом
 * з урахуванням апаратних відмінностей між ревізіями та виведення діагностики.
 */
class EspModuleController {
public:
    /**
     * @brief Конструктор контролера модуля.
     * @param revision Ревізія модуля (ESP-01 або ESP-01S).
     * @param uartConf Параметри конфігурації UART (за замовчуванням 115200 бод).
     */
    explicit EspModuleController(ModuleRevision revision, UartConfig uartConf = UartConfig{});

    /**
     * @brief Ініціалізує апаратні периферійні пристрої (UART та GPIO).
     */
    void begin();

    /**
     * @brief Встановлює стан вбудованого світлодіода.
     * @param turnOn true — увімкнути світлодіод, false — вимкнути.
     */
    void setLedState(bool turnOn);

    /**
     * @brief Перемикає стан світлодіода на протилежний.
     */
    void toggleLed();

    /**
     * @brief Повертає поточний логічний стан світлодіода.
     * @return true якщо світлодіод увімкнено, інакше false.
     */
    bool isLedOn() const;

    /**
     * @brief Виводить у UART детальну діагностичну інформацію про модуль та його стан.
     */
    void printDiagnosticInfo() const;

    /**
     * @brief Отримати ревізію модуля.
     */
    ModuleRevision getRevision() const;

    /**
     * @brief Отримати номер GPIO виводу світлодіода.
     */
    uint8_t getLedPin() const;

private:
    ModuleRevision m_revision;
    UartConfig m_uartConfig;
    LedConfig m_ledConfig;
    bool m_ledState{false}; ///< Логічний стан світлодіода (true = світиться)
};

#endif // ESP_MODULE_CONTROLLER_HPP
