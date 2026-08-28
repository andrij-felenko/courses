#include <cstdint>
#include <expected>
#include <string_view>
#include <memory>

namespace hal {

struct AccelerationVector {
    int16_t x{0};
    int16_t y{0};
    int16_t z{0};
};

enum class HardwareError : uint8_t {
    DeviceNotResponding,
    InvalidConfiguration,
    SelfTestFailed
};

/* Абстрактний базовий інтерфейс сенсора */
class IAccelerometer {
public:
    virtual ~IAccelerometer() = default;
    [[nodiscard]] virtual std::expected<void, HardwareError> initialize() noexcept = 0;
    [[nodiscard]] virtual std::expected<AccelerationVector, HardwareError> readAxes() noexcept = 0;
};

/* Конкретний драйвер для Rev A */
class Bmi160 final : public IAccelerometer {
public:
    std::expected<void, HardwareError> initialize() noexcept override {
        // Конфігурація регістрів BMI160 (0x68)
        return {};
    }

    std::expected<AccelerationVector, HardwareError> readAxes() noexcept override {
        return AccelerationVector{0, 0, 1000};
    }
};

/* Конкретний драйвер для Rev B та Rev C */
class Bmi270 final : public IAccelerometer {
public:
    std::expected<void, HardwareError> initialize() noexcept override {
        // Завантаження мікрокоду BMI270 (0x69)
        return {};
    }

    std::expected<AccelerationVector, HardwareError> readAxes() noexcept override {
        return AccelerationVector{1, -1, 998};
    }
};

/* Менеджер апаратних засобів з нульовою алокацією пам'яті */
class DeviceContext {
public:
    static DeviceContext& instance() noexcept {
        static DeviceContext ctx;
        return ctx;
    }

    [[nodiscard]] std::expected<void, HardwareError> configureForRevision(uint8_t revision) noexcept {
        if (revision == 1) {
            activeSensor_ = &bmi160_;
        } else if (revision == 2 || revision == 3) {
            activeSensor_ = &bmi270_;
        } else {
            return std::unexpected(HardwareError::InvalidConfiguration);
        }
        return activeSensor_->initialize();
    }

    [[nodiscard]] std::expected<AccelerationVector, HardwareError> getAcceleration() const noexcept {
        if (!activeSensor_) {
            return std::unexpected(HardwareError::DeviceNotResponding);
        }
        return activeSensor_->readAxes();
    }

private:
    DeviceContext() = default;
    Bmi160 bmi160_;
    Bmi270 bmi270_;
    IAccelerometer* activeSensor_{nullptr};
};

} // namespace hal
