#include <cstdint>
#include <concepts>
#include <expected>
#include <chrono>

namespace embedded::bus {

/**
 * @brief Типізовані статуси завершення відновлення шини I2C
 */
enum class RecoveryStatus : uint8_t {
    Success,
    SclStuckLow,
    SdaStuckLow,
    RecoveredViaPowerCycle,
    FatalHardwareFault
};

/**
 * @brief Концепт апаратного рівня доступу до виводів GPIO шини I2C
 */
template <typename T>
concept I2cPinController = requires(T hal, bool level, uint32_t us, uint32_t ms) {
    { hal.setSclModeOpenDrain() } -> std::same_as<void>;
    { hal.setSdaModeOpenDrain() } -> std::same_as<void>;
    { hal.setSclModeI2c() }       -> std::same_as<void>;
    { hal.setSdaModeI2c() }       -> std::same_as<void>;
    { hal.writeScl(level) }       -> std::same_as<void>;
    { hal.writeSda(level) }       -> std::same_as<void>;
    { hal.readScl() }             -> std::same_as<bool>;
    { hal.readSda() }             -> std::same_as<bool>;
    { hal.setPowerSwitch(level) } -> std::same_as<void>;
    { hal.delayUs(us) }           -> std::same_as<void>;
    { hal.delayMs(ms) }           -> std::same_as<void>;
};

/**
 * @brief RAII-обгортка для безпечного перемикання режимів пінів GPIO
 */
template <I2cPinController PinHal>
class GpioPinGuard {
public:
    explicit GpioPinGuard(PinHal& hal) : hal_(hal) {
        hal_.setSclModeOpenDrain();
        hal_.setSdaModeOpenDrain();
    }

    ~GpioPinGuard() {
        hal_.setSclModeI2c();
        hal_.setSdaModeI2c();
    }

    GpioPinGuard(const GpioPinGuard&) = delete;
    GpioPinGuard& operator=(const GpioPinGuard&) = delete;

private:
    PinHal& hal_;
};

/**
 * @brief Менеджер відновлення шини I2C з підтримкою C++20
 */
template <I2cPinController PinHal>
class I2cBusRecoveryManager {
public:
    struct Config {
        uint32_t clockDelayUs{5};
        uint8_t  maxClocks{9};
        uint32_t powerOffDurationMs{50};
        uint32_t powerSettleDurationMs{20};
    };

    explicit constexpr I2cBusRecoveryManager(PinHal& hal, Config cfg = {})
        : hal_(hal), config_(cfg) {}

    /**
     * @brief Запуск повного алгоритму діагностики та відновлення шини
     */
    [[nodiscard]] std::expected<RecoveryStatus, RecoveryStatus> recover() {
        // Рівень 1: Програмне відновлення через 9 тактів SCL
        {
            GpioPinGuard<PinHal> guard(hal_);
            auto result = execute9ClockSequence();
            if (result == RecoveryStatus::Success) {
                return RecoveryStatus::Success;
            }
        }

        // Рівень 2: Апаратний цикл скидання живлення (Power Cycle)
        return executeHardwarePowerCycle();
    }

private:
    [[nodiscard]] RecoveryStatus execute9ClockSequence() {
        hal_.writeScl(true);
        hal_.writeSda(true);
        hal_.delayUs(config_.clockDelayUs);

        // Перевірка на SCL Lockup
        if (!hal_.readScl()) {
            return RecoveryStatus::SclStuckLow;
        }

        bool sdaReleased = hal_.readSda();

        for (uint8_t pulse = 0; pulse < config_.maxClocks && !sdaReleased; ++pulse) {
            // SCL = LOW
            hal_.writeScl(false);
            hal_.delayUs(config_.clockDelayUs);

            // SCL = HIGH
            hal_.writeScl(true);
            hal_.delayUs(config_.clockDelayUs);

            // Контроль Clock Stretching
            uint32_t timeout = 100;
            while (!hal_.readScl() && timeout > 0) {
                hal_.delayUs(config_.clockDelayUs);
                --timeout;
            }
            if (timeout == 0) {
                return RecoveryStatus::SclStuckLow;
            }

            if (hal_.readSda()) {
                sdaReleased = true;
                break;
            }
        }

        if (!hal_.readSda()) {
            return RecoveryStatus::SdaStuckLow;
        }

        // Генерація умови STOP
        hal_.writeScl(false);
        hal_.delayUs(config_.clockDelayUs);
        hal_.writeSda(false);
        hal_.delayUs(config_.clockDelayUs);

        hal_.writeScl(true);
        hal_.delayUs(config_.clockDelayUs);
        hal_.writeSda(true);
        hal_.delayUs(config_.clockDelayUs);

        if (hal_.readScl() && hal_.readSda()) {
            return RecoveryStatus::Success;
        }

        return RecoveryStatus::SdaStuckLow;
    }

    [[nodiscard]] std::expected<RecoveryStatus, RecoveryStatus> executeHardwarePowerCycle() {
        // Правило 2: Переведення ліній у нуль перед знеструмленням
        hal_.setSclModeOpenDrain();
        hal_.setSdaModeOpenDrain();
        hal_.writeScl(false);
        hal_.writeSda(false);

        // Знеструмлення
        hal_.setPowerSwitch(false);
        hal_.delayMs(config_.powerOffDurationMs);

        // Подача живлення
        hal_.setPowerSwitch(true);
        hal_.delayMs(config_.powerSettleDurationMs);

        // Повторне тактування після холодного старту
        hal_.writeScl(true);
        hal_.writeSda(true);

        GpioPinGuard<PinHal> guard(hal_);
        auto result = execute9ClockSequence();

        if (result == RecoveryStatus::Success) {
            return RecoveryStatus::RecoveredViaPowerCycle;
        }

        return std::unexpected(RecoveryStatus::FatalHardwareFault);
    }

    PinHal& hal_;
    Config  config_;
};

} // namespace embedded::bus
