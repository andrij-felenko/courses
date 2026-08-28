#include <cstdint>
#include <array>
#include <span>
#include <expected>

enum class SensorError {
    BusFailure,
    InvalidDevice,
    ConfigurationFailed
};

class ImuDriver {
public:
    static constexpr uint8_t reg_who_am_i = 0x0F;
    static constexpr uint8_t expected_id  = 0x6C;
    static constexpr uint8_t reg_ctrl1_xl = 0x10;
    static constexpr uint8_t reg_status   = 0x1E;

    explicit ImuDriver(uint8_t exti_pin) : exti_pin_(exti_pin) {}

    std::expected<void, SensorError> safe_initialize() {
        uint8_t chip_id = 0;
        if (!read_register(reg_who_am_i, chip_id) || chip_id != expected_id) {
            return std::unexpected(SensorError::InvalidDevice);
        }

        // Крок відновлення: холостий змив (Dummy Flush) буферів і статусів
        std::array<uint8_t, 14> dummy_buffer{};
        if (!burst_read(reg_status, dummy_buffer)) {
            return std::unexpected(SensorError::BusFailure);
        }

        // Конфігурація ODR = 1000 Гц, фільтрація, дозвіл DRDY на виводі INT1
        if (!write_register(reg_ctrl1_xl, 0x80)) {
            return std::unexpected(SensorError::ConfigurationFailed);
        }

        // Контрольне скидання статусу
        uint8_t final_status = 0;
        read_register(reg_status, final_status);

        // Увімкнення апаратного детектора перепаду після очищення лінії
        hardware_enable_exti(exti_pin_);

        return {};
    }

private:
    uint8_t exti_pin_;

    bool read_register(uint8_t reg, uint8_t& val);
    bool write_register(uint8_t reg, uint8_t val);
    bool burst_read(uint8_t reg, std::span<uint8_t> buffer);
    void hardware_enable_exti(uint8_t pin);
};
