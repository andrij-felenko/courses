#include <cstdint>
#include <concepts>
#include <expected>
#include <chrono>

enum class BusError {
    SclStuckLow,
    SdaStuckLow,
    InvalidHardwareConfig
};

enum class RecoveryResult {
    AlreadyClean,
    SuccessfullyRecovered
};

template <typename HalPolicy>
concept I2cHalPolicy = requires(HalPolicy hal, bool state, uint32_t us) {
    { hal.set_scl(state) } -> std::same_as<void>;
    { hal.set_sda(state) } -> std::same_as<void>;
    { hal.read_scl() }     -> std::same_as<bool>;
    { hal.read_sda() }     -> std::same_as<bool>;
    { hal.delay_us(us) }   -> std::same_as<void>;
    { hal.reinit_hardware() } -> std::same_as<void>;
};

template <I2cHalPolicy Hal>
class ResilientI2cBus {
public:
    explicit ResilientI2cBus(Hal hal) : hal_(hal) {}

    [[nodiscard]] std::expected<RecoveryResult, BusError> recover_bus() noexcept {
        hal_.set_scl(true);
        hal_.set_sda(true);
        hal_.delay_us(5);

        // Якщо SCL на нулі — лінія фізично пошкоджена або ведений затиснув Clock Stretch
        if (!hal_.read_scl()) {
            return std::unexpected(BusError::SclStuckLow);
        }

        // Лінія SDA чиста — відновлення не потрібне
        if (hal_.read_sda()) {
            return RecoveryResult::AlreadyClean;
        }

        bool sda_released = false;
        constexpr uint8_t max_clocks = 9;

        for (uint8_t i = 0; i < max_clocks; ++i) {
            hal_.set_scl(false);
            hal_.delay_us(5);
            hal_.set_scl(true);
            hal_.delay_us(5);

            if (hal_.read_sda()) {
                sda_released = true;
                break;
            }
        }

        if (!sda_released) {
            return std::unexpected(BusError::SdaStuckLow);
        }

        // Генерація апаратної умови STOP для завершення стану транзакції
        hal_.set_sda(false);
        hal_.delay_us(5);
        hal_.set_scl(true);
        hal_.delay_us(5);
        hal_.set_sda(true);
        hal_.delay_us(5);

        // Повернення контролю апаратному блоку I2C
        hal_.reinit_hardware();

        return RecoveryResult::SuccessfullyRecovered;
    }

private:
    Hal hal_;
};
