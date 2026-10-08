#pragma once

#include <cstdint>
#include <cstddef>
#include <span>

namespace resolver {

/**
 * @brief Абстрактний інтерфейс для виконання SPI-транзакцій.
 * Забезпечує апаратну незалежність драйвера AD2S1210 від конкретної мікроконтролерної платформи (STM32, ESP32, AVR тощо).
 */
class ISpiDriver {
public:
    virtual ~ISpiDriver() = default;

    /**
     * @brief Повнодуплексна передача блоку даних через шину SPI.
     * @param tx_buf Буфер передачі (команди, адреси регістра або дані).
     * @param rx_buf Буфер прийому відповіді.
     * @return true при успішній передачі, false у разі помилки шини.
     */
    virtual bool transfer(std::span<const std::uint8_t> tx_buf, std::span<std::uint8_t> rx_buf) = 0;

    /**
     * @brief Передача одного байта по SPI із синхронним читанням відповіді.
     * @param tx_byte Байт для відправки.
     * @param rx_byte Посилання для збереження прийнятого байта.
     * @return true у разі успіху.
     */
    virtual bool transfer_byte(std::uint8_t tx_byte, std::uint8_t& rx_byte) = 0;
};

/**
 * @brief Абстрактний інтерфейс дискретних ліній GPIO для керування станами та режимами AD2S1210.
 */
class ISpiGpio {
public:
    virtual ~ISpiGpio() = default;

    /// Перелік керуючих дискретних пінів AD2S1210
    enum class Pin {
        CS,     ///< Chip Select (активний низький)
        A0,     ///< Вибір режиму bit 0
        A1,     ///< Вибір режиму bit 1
        SAMPLE, ///< Строб засувки вимірювань (активний низький)
        RESET   ///< Скидання мікросхеми (активний низький)
    };

    /// Логічний рівень виходу GPIO
    enum class Level {
        Low = 0,
        High = 1
    };

    /**
     * @brief Встановити стан дискретної лінії GPIO.
     * @param pin Ідентифікатор піна.
     * @param level Логічний рівень (High або Low).
     */
    virtual void write_pin(Pin pin, Level level) = 0;

    /**
     * @brief Програмна затримка в мікросекундах.
     * @param microseconds Тривалість затримки.
     */
    virtual void delay_us(std::uint32_t microseconds) = 0;
};

} // namespace resolver
