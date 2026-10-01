#ifndef ESP01_TESTER_HPP
#define ESP01_TESTER_HPP

#include <Arduino.h>

/**
 * @brief Перелік станів світлодіодного індикатора.
 */
enum class LedState : uint8_t {
    Off = 0,  ///< Світлодіод вимкнено
    On = 1    ///< Світлодіод увімкнено
};

/**
 * @brief Параметри конфігурації UART для діагностики ESP-01.
 */
struct UartConfig {
    uint32_t baudRate{115200}; ///< Швидкість передачі даних біт/с (за замовчуванням 115200)
};

/**
 * @brief Параметри конфігурації GPIO пінів ESP-01.
 */
struct GpioConfig {
    uint8_t ledPin{1};      ///< Номер GPIO піна світлодіода (GPIO1 для більшості ESP-01 або GPIO2 для ESP-01S)
    bool activeLow{true};   ///< Прапорець інверсної логіки (true: LOW = увімкнено, HIGH = вимкнено)
};

/**
 * @brief Клас для діагностики модуля ESP-01 та керування світлодіодною індикацією.
 *
 * Інкапсулює налаштування апаратного UART, інверсне керування вбудованим
 * світлодіодом та форматоване виведення відлагоджувальних повідомлень у Serial Monitor.
 */
class Esp01Tester {
public:
    /**
     * @brief Конструктор із можливістю задання конфігурацій UART та GPIO.
     * @param uartConf Налаштування послідовного порту.
     * @param gpioConf Налаштування пінів керування периферією.
     */
    explicit Esp01Tester(const UartConfig& uartConf = UartConfig{}, 
                         const GpioConfig& gpioConf = GpioConfig{});

    /**
     * @brief Первинна ініціалізація апаратного порту Serial та GPIO пінів.
     */
    void begin();

    /**
     * @brief Встановлює конкретний стан світлодіода (з урахуванням activeLow).
     * @param state Новий стан індикатора (LedState::On або LedState::Off).
     */
    void setLedState(LedState state);

    /**
     * @brief Перемикає поточний стан світлодіода на протилежний.
     */
    void toggleLed();

    /**
     * @brief Отримати поточний стан світлодіода.
     * @return Поточний стан LedState.
     */
    LedState getLedState() const;

    /**
     * @brief Виводить форматовану системну інформацію про ESP8266 у Serial Monitor.
     */
    void printSystemInfo() const;

    /**
     * @brief Виводить періодичне діагностичне повідомлення статус-серцебиття (Heartbeat).
     * @param cycleCount Номер поточного циклу виконання.
     */
    void printHeartbeat(uint32_t cycleCount) const;

private:
    UartConfig m_uartConfig;
    GpioConfig m_gpioConfig;
    LedState m_currentLedState{LedState::Off};

    /**
     * @brief Внутрішня функція запису фізичного рівня на GPIO пін.
     * @param state Стан індикатора.
     */
    void writeHardwarePin(LedState state);
};

#endif // ESP01_TESTER_HPP
