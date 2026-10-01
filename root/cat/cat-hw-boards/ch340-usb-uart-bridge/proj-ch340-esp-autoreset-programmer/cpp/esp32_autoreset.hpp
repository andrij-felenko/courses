#ifndef ESP32_AUTORESET_HPP
#define ESP32_AUTORESET_HPP

#include <string>
#include <string_view>
#include <chrono>
#include <stdexcept>

/**
 * @brief Клас для апаратного керування сигнальними лініями DTR та RTS
 *        USB-UART мосту CH340 для перезавантаження та входу у bootloader ESP32.
 */
class Esp32AutoReset {
public:
    /**
     * @brief Конструктор. Відкриває послідовний порт за вказаним шляхом (RAII).
     * @param port_path Шлях до пристрою (наприклад, "/dev/ttyUSB0")
     */
    explicit Esp32AutoReset(std::string_view port_path);

    /**
     * @brief Деструктор. Скидає стан ліній та закриває дескриптор порту.
     */
    ~Esp32AutoReset();

    /* Заборона копіювання (RAII ресурс) */
    Esp32AutoReset(const Esp32AutoReset&) = delete;
    Esp32AutoReset& operator=(const Esp32AutoReset&) = delete;

    /* Переміщення ресурсу */
    Esp32AutoReset(Esp32AutoReset&& other) noexcept;
    Esp32AutoReset& operator=(Esp32AutoReset&& other) noexcept;

    /**
     * @brief Переводить ESP32 у режим завантажника (Bootloader mode).
     * @param delay_ms Тривалість утримання імпульсу в мілісекундах (за замовчуванням 100 мс)
     */
    void enter_bootloader(std::chrono::milliseconds delay_ms = std::chrono::milliseconds(100));

    /**
     * @brief Виконує звичайне апаратне скидання мікроконтролера (Hard Reset).
     * @param reset_hold_ms Тривалість утримання скидання в мілісекундах
     */
    void hard_reset(std::chrono::milliseconds reset_hold_ms = std::chrono::milliseconds(50));

    /**
     * @brief Пряме керування станами ліній DTR та RTS.
     * @param dtr Стан лінії DTR (true — високий рівень / активний біт)
     * @param rts Стан лінії RTS (true — високий рівень / активний біт)
     */
    void set_lines(bool dtr, bool rts);

private:
    int m_fd{-1};
    std::string m_port_path;

    void configure_port();
};

#endif // ESP32_AUTORESET_HPP
