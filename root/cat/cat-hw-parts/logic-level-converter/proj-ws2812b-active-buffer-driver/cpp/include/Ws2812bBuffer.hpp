#ifndef WS2812B_BUFFER_HPP
#define WS2812B_BUFFER_HPP

#include <cstdint>
#include <vector>
#include <span>

/**
 * @file Ws2812bBuffer.hpp
 * @brief Оголошення класу Ws2812bBuffer для керування буфером 74AHCT125 та формування імпульсів WS2812B.
 */

namespace hardware {

/**
 * @brief Структура для представлення кольору пікселя у форматі GRB.
 */
struct Color {
    uint8_t g; ///< Зелена складова (Green)
    uint8_t r; ///< Червона складова (Red)
    uint8_t b; ///< Синя складова (Blue)
};

/**
 * @brief Налаштування таймінгів однопровідного протоколу WS2812B (у наносекундах).
 */
struct Ws2812Timings {
    uint32_t t0h_ns = 400; ///< Тривалість високого рівня для біта '0'
    uint32_t t0l_ns = 850; ///< Тривалість низького рівня для біта '0'
    uint32_t t1h_ns = 800; ///< Тривалість високого рівня для біта '1'
    uint32_t t1l_ns = 450; ///< Тривалість низького рівня для біта '1'
    uint32_t reset_us = 300; ///< Мінімальна тривалість скидання (Reset) у мікросекундах
};

/**
 * @brief Клас-обгортка RAII для керування односпрямованим буфером 74AHCT125 та передачі даних WS2812B.
 */
class Ws2812bBuffer {
public:
    /**
     * @brief Конструктор. Ініціалізує піни та переводить лінію /OE у стан HIGH (Hi-Z / вимкнено).
     * @param oe_pin Пін дозволу виходу (Output Enable) буфера 74AHCT125 (active-low).
     * @param data_pin Пін передачі даних до світлодіодної стрічки.
     */
    explicit Ws2812bBuffer(int oe_pin, int data_pin);

    /**
     * @brief Деструктор. Автоматично вимикає буфер (переводить /OE у HIGH / Hi-Z) для безпеки апаратного забезпечення.
     */
    ~Ws2812bBuffer();

    // Заборона копіювання задля безпеки керування апаратними ресурсами RAII
    Ws2812bBuffer(const Ws2812bBuffer&) = delete;
    Ws2812bBuffer& operator=(const Ws2812bBuffer&) = delete;

    // Дозволено переміщення
    Ws2812bBuffer(Ws2812bBuffer&& other) noexcept;
    Ws2812bBuffer& operator=(Ws2812bBuffer&& other) noexcept;

    /**
     * @brief Активує буфер (переводить пін /OE у LOW), дозволяючи передачу 5В сигналів на стрічку.
     */
    void enable();

    /**
     * @brief Деактивує буфер (переводить пін /OE у HIGH), переводячи виходи у високоімпедансний стан (Hi-Z).
     */
    void disable();

    /**
     * @brief Перевіряє, чи активований буфер.
     * @return true, якщо буфер увімкнено, і false інакше.
     */
    [[nodiscard]] bool isEnabled() const noexcept;

    /**
     * @brief Передає послідовність пікселів на світлодіодну стрічку.
     * @param pixels Масив пікселів для передачі (формат GRB).
     */
    void sendPixels(std::span<const Color> pixels);

    /**
     * @brief Формує імпульс скидання (Reset) для защолкнення кадру стрічкою.
     */
    void sendReset();

    /**
     * @brief Встановлює кастомні таймінги протоколу.
     * @param timings Нові значення таймінгів.
     */
    void setTimings(const Ws2812Timings& timings) noexcept;

private:
    int oe_pin_;       ///< Номер піна /OE буфера 74AHCT125
    int data_pin_;     ///< Номер піна даних стрічки
    bool is_enabled_;  ///< Поточний стан буфера
    Ws2812Timings timings_; ///< Часові параметри протоколу WS2812B

    /**
     * @brief Низкорівневий метод виведення одного біта з прецизійними затримками.
     * @param bit Логічний біт для відправки (true = '1', false = '0').
     */
    void writeBit(bool bit);
};

} // namespace hardware

#endif // WS2812B_BUFFER_HPP
