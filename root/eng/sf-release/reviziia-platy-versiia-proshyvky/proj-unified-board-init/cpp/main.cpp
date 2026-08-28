#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <expected>
#include <string_view>
#include <array>

namespace board {

enum class Revision : uint8_t {
    Unknown = 0,
    RevA    = 1,
    RevB    = 2,
    RevC    = 3
};

struct ImuSample {
    int16_t x{0};
    int16_t y{0};
    int16_t z{0};
};

enum class DriverError : uint8_t {
    DeviceNotFound,
    BusTimeout,
    HardwareFault,
    InvalidParameter
};

/* Чистий поліморфний інтерфейс датчика руху */
class IImuDriver {
public:
    virtual ~IImuDriver() = default;
    [[nodiscard]] virtual std::expected<void, DriverError> init() noexcept = 0;
    [[nodiscard]] virtual std::expected<ImuSample, DriverError> readAcceleration() noexcept = 0;
    [[nodiscard]] virtual std::expected<void, DriverError> sleep() noexcept = 0;
};

/* Чистий поліморфний інтерфейс енергонезалежної Flash-пам'яті */
class IFlashDriver {
public:
    virtual ~IFlashDriver() = default;
    [[nodiscard]] virtual std::expected<void, DriverError> init(uint8_t csPin) noexcept = 0;
    [[nodiscard]] virtual std::expected<void, DriverError> read(uint32_t addr, std::span<uint8_t> buffer) noexcept = 0;
    [[nodiscard]] virtual std::expected<void, DriverError> write(uint32_t addr, std::span<const uint8_t> buffer) noexcept = 0;
    [[nodiscard]] virtual std::expected<void, DriverError> eraseSector(uint32_t addr) noexcept = 0;
};

/* Реалізація драйвера Bosch BMI160 для Rev A */
class Bmi160Driver final : public IImuDriver {
public:
    std::expected<void, DriverError> init() noexcept override {
        return {};
    }
    std::expected<ImuSample, DriverError> readAcceleration() noexcept override {
        return ImuSample{10, 20, 980};
    }
    std::expected<void, DriverError> sleep() noexcept override {
        return {};
    }
};

/* Реалізація драйвера Bosch BMI270 для Rev B та Rev C */
class Bmi270Driver final : public IImuDriver {
public:
    std::expected<void, DriverError> init() noexcept override {
        return {};
    }
    std::expected<ImuSample, DriverError> readAcceleration() noexcept override {
        return ImuSample{12, 22, 981};
    }
    std::expected<void, DriverError> sleep() noexcept override {
        return {};
    }
};

/* Реалізація драйвера Winbond W25Q128 */
class W25qDriver final : public IFlashDriver {
public:
    std::expected<void, DriverError> init(uint8_t /*csPin*/) noexcept override {
        return {};
    }
    std::expected<void, DriverError> read(uint32_t /*addr*/, std::span<uint8_t> /*buffer*/) noexcept override {
        return {};
    }
    std::expected<void, DriverError> write(uint32_t /*addr*/, std::span<const uint8_t> /*buffer*/) noexcept override {
        return {};
    }
    std::expected<void, DriverError> eraseSector(uint32_t /*addr*/) noexcept override {
        return {};
    }
};

/* Реалізація драйвера Macronix MX25L128 */
class Mx25lDriver final : public IFlashDriver {
public:
    std::expected<void, DriverError> init(uint8_t /*csPin*/) noexcept override {
        return {};
    }
    std::expected<void, DriverError> read(uint32_t /*addr*/, std::span<uint8_t> /*buffer*/) noexcept override {
        return {};
    }
    std::expected<void, DriverError> write(uint32_t /*addr*/, std::span<const uint8_t> /*buffer*/) noexcept override {
        return {};
    }
    std::expected<void, DriverError> eraseSector(uint32_t /*addr*/) noexcept override {
        return {};
    }
};

/* Дескриптор платформи з нульовою динамічною алокацією пам'яті */
struct PlatformDescriptor {
    Revision revision;
    std::string_view modelName;
    uint8_t spiChipSelectPin;
    IImuDriver& imuRef;
    IFlashDriver& flashRef;
};

/* Синглтони екземплярів драйверів у статичній пам'яті */
inline Bmi160Driver g_bmi160;
inline Bmi270Driver g_bmi270;
inline W25qDriver   g_w25q;
inline Mx25lDriver  g_mx25l;

constexpr std::array<PlatformDescriptor, 3> PLATFORM_TABLE{{
    { Revision::RevA, "Board Rev A (2023)", 4,  g_bmi160, g_w25q },
    { Revision::RevB, "Board Rev B (2024)", 4,  g_bmi270, g_w25q },
    { Revision::RevC, "Board Rev C (2025)", 13, g_bmi270, g_mx25l }
}};

/* Менеджер конфігурації заліза */
class BoardManager {
public:
    static constexpr Revision decodeAdcVoltage(uint16_t adcRaw) noexcept {
        if (adcRaw < 400) {
            return Revision::RevA;
        } else if (adcRaw >= 1700 && adcRaw <= 2400) {
            return Revision::RevB;
        } else if (adcRaw >= 3700) {
            return Revision::RevC;
        }
        return Revision::Unknown;
    }

    [[nodiscard]] std::expected<void, DriverError> earlyInit(uint16_t adcValue) noexcept {
        const auto rev = decodeAdcVoltage(adcValue);
        if (rev == Revision::Unknown) {
            return std::unexpected(DriverError::HardwareFault);
        }

        for (const auto& platform : PLATFORM_TABLE) {
            if (platform.revision == rev) {
                currentPlatform_ = &platform;
                
                auto imuRes = currentPlatform_->imuRef.init();
                if (!imuRes) return std::unexpected(imuRes.error());

                auto flashRes = currentPlatform_->flashRef.init(currentPlatform_->spiChipSelectPin);
                if (!flashRes) return std::unexpected(flashRes.error());

                return {};
            }
        }

        return std::unexpected(DriverError::DeviceNotFound);
    }

    [[nodiscard]] std::expected<ImuSample, DriverError> getAcceleration() const noexcept {
        if (!currentPlatform_) {
            return std::unexpected(DriverError::HardwareFault);
        }
        return currentPlatform_->imuRef.readAcceleration();
    }

    [[nodiscard]] std::string_view getBoardName() const noexcept {
        return currentPlatform_ ? currentPlatform_->modelName : "Uninitialized";
    }

private:
    const PlatformDescriptor* currentPlatform_{nullptr};
};

} // namespace board
