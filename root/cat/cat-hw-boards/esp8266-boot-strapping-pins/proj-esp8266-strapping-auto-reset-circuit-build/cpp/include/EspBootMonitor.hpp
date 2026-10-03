#pragma once

#include <Arduino.h>
#include <cstdint>

/**
 * @brief Перелік режимів завантаження мікроконтролера ESP8266,
 * які визначаються логічними рівнями на конфігураційних виводах (GPIO0, GPIO2, GPIO15)
 * у момент подачі живлення або скидання (Reset).
 */
enum class BootMode : uint8_t {
    SpiFlash,     ///< Запуск із зовнішньої SPI Flash пам'яті (GPIO15=0, GPIO0=1, GPIO2=1)
    UartDownload, ///< Запуск внутрішнього UART-завантажувача для прошивки (GPIO15=0, GPIO0=0, GPIO2=1)
    SdCard,       ///< Запуск із SD-карти через інтерфейс SDIO (GPIO15=1)
    Invalid       ///< Неприпустима комбінація виводів (наприклад, GPIO2=0)
};

/**
 * @brief Структурний звіт про стан конфігураційних виводів завантаження (strapping pins)
 * та причини апаратного скидання ESP8266.
 */
struct BootStatusReport {
    bool gpio0State{false};           ///< Логічний рівень на GPIO0 (0 = LOW, 1 = HIGH)
    bool gpio2State{false};           ///< Логічний рівень на GPIO2 (0 = LOW, 1 = HIGH)
    bool gpio15State{false};          ///< Логічний рівень на GPIO15 (0 = LOW, 1 = HIGH)
    BootMode mode{BootMode::Invalid}; ///< Визначений режим завантаження
    uint32_t resetReasonRaw{0};       ///< Числовий код причини скидання від rst_info
    String resetReasonStr;            ///< Текстовий опис причини скидання системи

    /**
     * @brief Формує розширений текстовий звіт для передачі через послідовний порт UART.
     * @return Текстовий рядок із детальною діагностичною інформацією.
     */
    String toString() const;
};

/**
 * @brief Клас для моніторингу конфігураційних виводів завантаження (boot-strapping pins)
 * та аналізу причин перезавантаження ESP8266.
 */
class EspBootMonitor {
public:
    // Номери виводів boot-strapping для ESP8266
    static constexpr uint8_t PIN_GPIO0  = 0;
    static constexpr uint8_t PIN_GPIO2  = 2;
    static constexpr uint8_t PIN_GPIO15 = 15;

    EspBootMonitor() = default;

    /**
     * @brief Ініціалізує підтягувальні резистори виводів та фіксує початковий стан системи під час старту.
     */
    void begin();

    /**
     * @brief Отримує збережений під час ініціалізації звіт про завантаження.
     * @return Структура BootStatusReport з фіксованими при старті даними.
     */
    BootStatusReport getInitialBootReport() const;

    /**
     * @brief Здійснює поточне (динамічне) зчитування станів виводів без впливу на початковий режим.
     * @return Поточний стан виводів у вигляді BootStatusReport.
     */
    BootStatusReport sampleCurrentState() const;

    /**
     * @brief Визначає режим завантаження ESP8266 на основі логічних рівнів виводів.
     * @param g0 Стан GPIO0
     * @param g2 Стан GPIO2
     * @param g15 Стан GPIO15
     * @return Режим завантаження BootMode
     */
    static BootMode evaluateBootMode(bool g0, bool g2, bool g15);

    /**
     * @brief Перетворює значення переліку BootMode у текстовий опис українською мовою.
     * @param mode Режим завантаження
     * @return Константний символьний рядок з описом режиму.
     */
    static const char* bootModeToString(BootMode mode);

private:
    BootStatusReport initialReport;
    bool isInitialized{false};

    /**
     * @brief Зчитує апаратну причину скидання системи з системного регістра ESP8266.
     * @param rawCode Вихідний параметр для збереження числового коду.
     * @return Текстовий рядок з описом причини скидання.
     */
    String fetchResetReason(uint32_t& rawCode) const;
};
