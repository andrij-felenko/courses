#include <cstdint>
#include <optional>
#include <concepts>

namespace fieldbus {

enum class BusType {
    I2c,
    Can,
    Rs485
};

enum class BusState {
    Ok,
    Warning,
    Stuck,
    Recovering,
    Fatal
};

// Концепт для апаратного рівня відновлення I2C
template <typename T>
concept I2cLowLevelDriver = requires(T dev, bool state, uint32_t us) {
    { dev.setScl(state) } -> std::same_as<void>;
    { dev.setSda(state) } -> std::same_as<void>;
    { dev.getScl() } -> std::same_as<bool>;
    { dev.getSda() } -> std::same_as<bool>;
    { dev.setGpioOpenDrainMode() } -> std::same_as<void>;
    { dev.setHardwarePeripheralMode() } -> std::same_as<void>;
    { dev.setPowerEnable(state) } -> std::same_as<void>;
    { dev.delayMicroseconds(us) } -> std::same_as<void>;
};

// RAII-клас автоматичного відновлення I2C
template <I2cLowLevelDriver Driver>
class I2cBusRecovery {
public:
    explicit I2cBusRecovery(Driver& drv) : driver_(drv) {}

    [[nodiscard]] bool recover() noexcept {
        driver_.setGpioOpenDrainMode();
        driver_.setScl(true);
        driver_.setSda(true);
        driver_.delayMicroseconds(10);

        // Якщо шина вже чиста — повертаємося в апаратний режим
        if (driver_.getSda() && driver_.getScl()) {
            driver_.setHardwarePeripheralMode();
            return true;
        }

        // 1. Подаємо до 9 тактів SCL для виштовхування застряглого біта
        for (int cycle = 0; cycle < 9; ++cycle) {
            driver_.setScl(false);
            driver_.delayMicroseconds(10);
            driver_.setScl(true);
            driver_.delayMicroseconds(10);

            if (driver_.getSda()) {
                break; // Ведений пристрій відпустив SDA
            }
        }

        // 2. Генеруємо легітимну умову STOP (перепад SDA 0->1 при SCL=1)
        driver_.setSda(false);
        driver_.delayMicroseconds(10);
        driver_.setScl(true);
        driver_.delayMicroseconds(10);
        driver_.setSda(true);
        driver_.delayMicroseconds(10);

        bool success = driver_.getSda() && driver_.getScl();

        // 3. Fallback: якщо шина заблокована наглухо — скидаємо живлення датчиків
        if (!success) {
            driver_.setPowerEnable(false);
            driver_.delayMicroseconds(15000); // 15 мс розряд ємностей
            driver_.setPowerEnable(true);
            driver_.delayMicroseconds(10000); // 10 мс стабілізація живлення
            success = driver_.getSda() && driver_.getScl();
        }

        driver_.setHardwarePeripheralMode();
        return success;
    }

private:
    Driver& driver_;
};

// Концепт драйвера CAN для контролю Bus-Off
template <typename T>
concept CanLowLevelDriver = requires(T dev) {
    { dev.getTransmitErrorCount() } -> std::same_as<uint32_t>;
    { dev.getReceiveErrorCount() } -> std::same_as<uint32_t>;
    { dev.isBusOff() } -> std::same_as<bool>;
    { dev.resetHardware() } -> std::same_as<void>;
    { dev.startHardware() } -> std::same_as<void>;
};

template <CanLowLevelDriver Driver>
class CanBusWatchdog {
public:
    explicit CanBusWatchdog(Driver& drv) : driver_(drv) {}

    void update(uint32_t currentTickMs) noexcept {
        if (driver_.isBusOff()) {
            state_ = BusState::Stuck;

            if (currentTickMs - lastRecoveryTick_ >= backoffDelayMs_) {
                lastRecoveryTick_ = currentTickMs;
                ++consecutiveFailures_;
                updateBackoffDelay();

                driver_.resetHardware();
                driver_.startHardware();
                state_ = BusState::Recovering;
            }
        } else {
            const auto tec = driver_.getTransmitErrorCount();
            const auto rec = driver_.getReceiveErrorCount();

            if (tec < 96 && rec < 96) {
                state_ = BusState::Ok;
                consecutiveFailures_ = 0;
                backoffDelayMs_ = 50;
            } else if (tec >= 128 || rec >= 128) {
                state_ = BusState::Warning;
            }
        }
    }

    [[nodiscard]] BusState getState() const noexcept { return state_; }
    [[nodiscard]] uint32_t getFailures() const noexcept { return consecutiveFailures_; }

private:
    void updateBackoffDelay() noexcept {
        switch (consecutiveFailures_) {
            case 1:  backoffDelayMs_ = 50;   break;
            case 2:  backoffDelayMs_ = 200;  break;
            case 3:  backoffDelayMs_ = 1000; break;
            default: backoffDelayMs_ = 5000; break;
        }
    }

    Driver& driver_;
    BusState state_{BusState::Ok};
    uint32_t lastRecoveryTick_{0};
    uint32_t backoffDelayMs_{50};
    uint32_t consecutiveFailures_{0};
};

} // namespace fieldbus
