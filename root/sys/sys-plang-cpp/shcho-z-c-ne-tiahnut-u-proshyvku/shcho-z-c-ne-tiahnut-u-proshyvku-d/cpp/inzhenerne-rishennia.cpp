#include <cstdint>
#include <expected>

/* Типобезпечні помилки АЦП */
enum class AdcError : uint8_t {
    InvalidChannel,
    Timeout,
    Overvoltage
};

/* Обробка помилки через значення без динамічної пам'яті та винятків */
[[nodiscard]] constexpr std::expected<uint16_t, AdcError> 
adc_read_voltage(uint32_t channel) noexcept {
    if (channel > 15) {
        return std::unexpected(AdcError::InvalidChannel);
    }
    /* Результат повертається безпосередньо через регістр процесора R0 */
    return static_cast<uint16_t>(3300);
}

/* Монадичний ланцюжок обробки без винятків */
[[nodiscard]] constexpr std::expected<float, AdcError>
get_calibrated_voltage(uint32_t channel) noexcept {
    return adc_read_voltage(channel)
        .transform([](uint16_t raw_mv) noexcept {
            return static_cast<float>(raw_mv) * 0.001f;
        });
}
