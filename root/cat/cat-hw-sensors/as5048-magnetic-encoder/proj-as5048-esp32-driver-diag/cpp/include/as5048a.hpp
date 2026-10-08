#ifndef AS5048A_HPP
#define AS5048A_HPP

#include <cstdint>
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "esp_err.h"
#include "nvs.h"

namespace encoder {

/**
 * @brief Структура діагностичного стану магнітного поля та AGC давача AS5048A.
 */
struct DiagnosticStatus {
    uint8_t agc{0};             ///< Рівень AGC (0..255). Оптимальні значення ~128
    bool ocf{false};            ///< Offset Compensation Finished (1 = автокалібрування завершено)
    bool cof{false};            ///< CORDIC Overflow (1 = переповнення обчислювача кута)
    bool comp_low{false};       ///< Магнітне поле занадто слабке (магніт задалеко)
    bool comp_high{false};      ///< Магнітне поле занадто сильне (магніт заблизько)
    bool parity_error{false};   ///< Помилка парності в отриманому SPI-кадрі
    bool hardware_error{false}; ///< Прапорець помилки EF від AS5048A
};

/**
 * @brief Структура деталізованих помилок з регістру CLEAR ERROR (0x0001).
 */
struct ErrorFlags {
    bool framing_error{false};   ///< Помилка кількості тактових імпульсів SCLK
    bool command_invalid{false}; ///< Некоректна команда або адреса регістру
    bool parity_error{false};    ///< Помилка парності переданої команди
};

/**
 * @brief Драйвер 14-бітного магнітного енкодера кута AS5048A.
 * 
 * Забезпечує обмін по SPI з обчисленням парності, конвеєрне зчитування
 * кута без затримок для систем керування рухом під FreeRTOS (ESP-IDF)
 * та персистентне збереження калібрувального зміщення в NVS.
 */
class AS5048A {
public:
    /// Константа роздільної здатності енкодера (14 біт = 16384 відліки)
    static constexpr uint16_t K_MAX_ANGLE_RAW = 16384;

    /// Адреси регістрів AS5048A (14-бітний простір адресації)
    enum class Register : uint16_t {
        Nop             = 0x0000,
        ClearError      = 0x0001,
        ProgrammingCtrl = 0x0003,
        OtpZeroHigh     = 0x3FE0,
        OtpZeroLow      = 0x3FE1,
        DiagnosticsAgc  = 0x3FFE,
        Angle           = 0x3FFF,
        Magnitude       = 0x3FFD
    };

    /**
     * @brief Конструктор драйвера.
     * @param spi_host SPI периферичний модуль (наприклад, SPI2_HOST)
     * @param cs_pin GPIO номер лінії Chip Select
     */
    AS5048A(spi_host_device_t spi_host, gpio_num_t cs_pin);

    ~AS5048A();

    // Видаляємо конструктор копіювання для уникнення дублювання шинних дескрипторів
    AS5048A(const AS5048A&) = delete;
    AS5048A& operator=(const AS5048A&) = delete;

    /**
     * @brief Ініціалізація пристрою на SPI-шині та завантаження калібрування з NVS.
     * @return esp_err_t ESP_OK у разі успіху
     */
    esp_err_t begin();

    /**
     * @brief Конвеєрне зчитування сирого 14-бітного кута (Pipelined SPI).
     * 
     * Надсилає запит на зчитування кута (0x3FFF) та повертає результат попередньої
     * SPI-транзакції. Забезпечує максимальну частоту опитування без проміжних пауз.
     * 
     * @param[out] raw_angle Сире значення 14-бітного кута (0..16383)
     * @return true якщо отриманий кадр коректний (парність та прапорці помилок OK)
     */
    bool read_angle_pipelined(uint16_t& raw_angle);

    /**
     * @brief Зчитування відкаліброваного кута у градусах (0.0 .. 360.0).
     * @param[out] degrees Градуси кута з урахуванням збереженого нуля
     * @return true якщо кадр успішно зчитано
     */
    bool read_angle_degrees(float& degrees);

    /**
     * @brief Зчитування діагностичного стану (AGC, сила поля, OCF, COF).
     * @param[out] status Заповнювана структура діагностики
     * @return true якщо зчитування успішне
     */
    bool read_diagnostics(DiagnosticStatus& status);

    /**
     * @brief Зчитування та скидання регістру помилок AS5048A (Clear Error Flag 0x0001).
     * @param[out] errors Розшифрований вміст прапорців помилки
     * @return true у разі успіху
     */
    bool clear_errors(ErrorFlags& errors);

    /**
     * @brief Зафіксувати поточну позицію як новий нуль та зберегти в NVS.
     * @return esp_err_t ESP_OK при успішному записі в NVS
     */
    esp_err_t calibrate_zero_position();

    /**
     * @brief Встановити нульове зміщення ручним значенням.
     * @param offset 14-бітне значення зміщення (0..16383)
     * @param save_to_nvs Чи записувати значення в NVS
     */
    esp_err_t set_zero_offset(uint16_t offset, bool save_to_nvs = true);

    /**
     * @brief Отримати поточне нульове зміщення.
     */
    [[nodiscard]] uint16_t get_zero_offset() const { return zero_offset_; }

    /**
     * @brief Розрахунок парності для 16-бітного слова.
     * @param val 16-бітне слово
     * @return true якщо кількість 1-бітів ПАРНА
     */
    static bool is_even_parity(uint16_t val);

private:
    /**
     * @brief Формування 16-бітної команди читання з розрахованим бітом парності.
     * @param reg Адреса регістру
     */
    static uint16_t build_read_command(Register reg);

    /**
     * @brief Виконання повнодуплексного 16-бітного SPI-обміну.
     * @param tx_word Команда для передачі
     * @return uint16_t Відповідь від давача
     */
    uint16_t spi_transfer16(uint16_t tx_word);

    /**
     * @brief Завантаження калібрувального нуля з NVS.
     */
    esp_err_t load_zero_offset_from_nvs();

    /**
     * @brief Збереження калібрувального нуля в NVS.
     */
    esp_err_t save_zero_offset_to_nvs(uint16_t offset);

    spi_host_device_t spi_host_;
    gpio_num_t cs_pin_;
    spi_device_handle_t spi_device_{nullptr};

    uint16_t zero_offset_{0};      ///< Збережене 14-бітне нульове зміщення
    bool pipelined_active_{false}; ///< Стан конвеєрної послідовності SPI
};

} // namespace encoder

#endif // AS5048A_HPP
