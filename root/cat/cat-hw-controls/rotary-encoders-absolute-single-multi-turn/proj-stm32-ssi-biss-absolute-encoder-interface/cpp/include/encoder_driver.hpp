#ifndef ENCODER_DRIVER_HPP
#define ENCODER_DRIVER_HPP

#include <cstdint>

namespace encoder {

/// Протокол зв'язку з енкодером
enum class EncoderProtocol : std::uint8_t {
    SSI,    ///< Synchronous Serial Interface
    BiSSC   ///< Bidirectional Synchronous Serial (Mode C)
};

/// Кодування даних позиції
enum class DataEncoding : std::uint8_t {
    Binary, ///< Прямий двійковий код
    Gray    ///< Код Ґрея
};

/// Статус обробки кадру енкодера
enum class EncoderStatus : std::uint8_t {
    Ok = 0,             ///< Успішна обробка, дані коректні
    CrcError,           ///< Помилка контрольної суми CRC
    HardwareError,      ///< Апаратна відмова енкодера (nERROR = 0)
    WarningLowLight,    ///< Попередження про забруднення диска або низький заряд (nWARN = 0)
    InvalidConfig       ///< Некоректні конфігураційні параметри
};

/// Конфігураційні параметри абсолютного енкодера
struct EncoderConfig {
    EncoderProtocol protocol{EncoderProtocol::BiSSC};
    DataEncoding encoding{DataEncoding::Gray};
    std::uint8_t singleturn_bits{17};  ///< Розрядність однооборотного відліку (напр. 17 біт = 131072)
    std::uint8_t multiturn_bits{12};   ///< Розрядність лічильника обертів (напр. 12 біт = 4096)
    bool has_error_bit{true};          ///< Наявність біта апаратної помилки nERROR
    bool has_warn_bit{true};           ///< Наявність біта попередження nWARN
    std::uint8_t crc_poly{0x43};       ///< Поліном CRC-6 для BiSS-C: x^6 + x + 1 (0x43 із інверсією)
};

/// Результат розбору кадру енкодера
struct EncoderData {
    std::uint32_t singleturn_pos{0};   ///< Однооборотна абсолютна позиція [0 .. 2^ST - 1]
    std::uint32_t multiturn_count{0};  ///< Лічильник повних обертів [0 .. 2^MT - 1]
    std::uint64_t full_position{0};    ///< Сумарна розрахована позиція
    std::uint64_t relative_position{0};///< Позиція з урахуванням оффсету віртуального нуля
    bool error_flag{false};            ///< Ознака неклієнтської апаратної відмови
    bool warning_flag{false};          ///< Ознака попередження
    EncoderStatus status{EncoderStatus::Ok};
};

/// Перетворення коду Ґрея в двійковий код (constexpr, без винятків)
[[nodiscard]] constexpr std::uint64_t grayToBinary(std::uint64_t gray_val) noexcept {
    std::uint64_t bin = gray_val;
    for (std::uint64_t mask = gray_val >> 1; mask != 0; mask >>= 1) {
        bin ^= mask;
    }
    return bin;
}

/// Обчислення контрольної суми CRC-6 за специфікацією BiSS-C (x^6 + x + 1)
[[nodiscard]] constexpr std::uint8_t calcCrc6(std::uint64_t data, std::uint8_t bit_length) noexcept {
    std::uint8_t crc = 0x00; // Початковий стан 0 для BiSS-C
    for (int i = bit_length - 1; i >= 0; --i) {
        std::uint8_t bit = static_cast<std::uint8_t>((data >> i) & 1U);
        std::uint8_t crc_msb = static_cast<std::uint8_t>((crc >> 5) & 1U);
        crc = static_cast<std::uint8_t>((crc << 1) & 0x3FU);
        if ((crc_msb ^ bit) != 0U) {
            crc ^= 0x03U; // Поліном x^6 + x + 1 (маска 0x03 без MSB)
        }
    }
    return static_cast<std::uint8_t>(crc ^ 0x3FU); // Інверсія виходу BiSS-C
}

/// Клас драйвера абсолютного енкодера
class AbsoluteEncoder {
public:
    explicit AbsoluteEncoder(const EncoderConfig& config) noexcept;

    /// Обробка 64-бітного сирого кадру, прийнятого через SPI
    [[nodiscard]] EncoderStatus processFrame(std::uint64_t raw_frame, EncoderData& out_data) noexcept;

    /// Установка поточного положення як віртуального нуля
    void setZeroOffset(std::uint64_t current_full_pos) noexcept;

    /// Отримання поточного зміщення віртуального нуля
    [[nodiscard]] std::uint64_t getZeroOffset() const noexcept;

private:
    EncoderConfig config_;
    std::uint64_t zero_offset_{0};
    std::uint64_t position_mask_{0};
};

} // namespace encoder

#endif // ENCODER_DRIVER_HPP
