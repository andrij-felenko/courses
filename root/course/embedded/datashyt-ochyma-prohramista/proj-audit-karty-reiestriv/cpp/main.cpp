#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <concepts>

namespace driver {

/* Типізовані оффсети регістрів чипа */
enum class Reg : uint8_t {
    WhoAmI       = 0x0F,
    Ctrl1        = 0x20,
    Ctrl2        = 0x21,
    Status       = 0x27,
    OutXL        = 0x28,
    OutXH        = 0x29,
    OutYL        = 0x2A,
    OutYH        = 0x2B,
    OutZL        = 0x2C,
    OutZH        = 0x2D
};

/* Концепт абстракції апаратного транспорту шини */
template <typename T>
concept BusTransport = requires(T transport, uint8_t dev_addr, Reg reg, std::span<uint8_t> rx, std::span<const uint8_t> tx) {
    { transport.read(dev_addr, reg, rx) } -> std::same_as<bool>;
    { transport.write(dev_addr, reg, tx) } -> std::same_as<bool>;
};

enum class SensorError {
    BusError,
    InvalidDeviceIdentifier,
    RegisterVerificationMismatch,
    DataNotReady,
    OverrunDetected
};

struct AccelSample {
    float x_ms2;
    float y_ms2;
    float z_ms2;
};

template <BusTransport Transport>
class AccelSensor {
public:
    constexpr explicit AccelSensor(Transport& transport, uint8_t dev_addr = 0x6A) noexcept
        : transport_(transport), dev_addr_(dev_addr) {}

    /* 1. Верифікація ID чипа */
    [[nodiscard]] std::expected<void, SensorError> verify_identity() noexcept {
        uint8_t id = 0;
        if (!read_single_reg(Reg::WhoAmI, id)) {
            return std::unexpected(SensorError::BusError);
        }
        if (id != ExpectedChipId) {
            return std::unexpected(SensorError::InvalidDeviceIdentifier);
        }
        return {};
    }

    /* 2. Аудит запису конфігураційних регістрів */
    [[nodiscard]] std::expected<void, SensorError> audit_configuration() noexcept {
        constexpr uint8_t test_mask = Ctrl1Odr100Hz | Ctrl1AxesXyz;
        if (!write_single_reg(Reg::Ctrl1, test_mask)) {
            return std::unexpected(SensorError::BusError);
        }

        uint8_t readback = 0;
        if (!read_single_reg(Reg::Ctrl1, readback)) {
            return std::unexpected(SensorError::BusError);
        }

        if (readback != test_mask) {
            return std::unexpected(SensorError::RegisterVerificationMismatch);
        }
        return {};
    }

    /* 3. Ініціалізація BDU та діапазону чутливості */
    [[nodiscard]] std::expected<void, SensorError> initialize() noexcept {
        constexpr uint8_t ctrl2_val = Ctrl2BduEnable | Ctrl2Fsr2G;
        if (!write_single_reg(Reg::Ctrl2, ctrl2_val)) {
            return std::unexpected(SensorError::BusError);
        }

        constexpr uint8_t ctrl1_val = Ctrl1Odr100Hz | Ctrl1AxesXyz;
        if (!write_single_reg(Reg::Ctrl1, ctrl1_val)) {
            return std::unexpected(SensorError::BusError);
        }
        return {};
    }

    /* 4. Пакетне вичитування осей */
    [[nodiscard]] std::expected<AccelSample, SensorError> read_acceleration() noexcept {
        uint8_t buffer[6] = {};
        /* Встановлюємо старший біт адреси для автоінкременту в I2C */
        const auto burst_reg = static_cast<Reg>(static_cast<uint8_t>(Reg::OutXL) | AutoIncrementFlag);

        if (!transport_.read(dev_addr_, burst_reg, std::span{buffer})) {
            return std::unexpected(SensorError::BusError);
        }

        const auto raw_x = static_cast<int16_t>(static_cast<uint16_t>(buffer[0]) | (static_cast<uint16_t>(buffer[1]) << 8));
        const auto raw_y = static_cast<int16_t>(static_cast<uint16_t>(buffer[2]) | (static_cast<uint16_t>(buffer[3]) << 8));
        const auto raw_z = static_cast<int16_t>(static_cast<uint16_t>(buffer[4]) | (static_cast<uint16_t>(buffer[5]) << 8));

        constexpr float Sensitivity = 0.000061f; // 0.061 мг/LSB
        constexpr float Gravity = 9.80665f;

        return AccelSample{
            .x_ms2 = static_cast<float>(raw_x) * Sensitivity * Gravity,
            .y_ms2 = static_cast<float>(raw_y) * Sensitivity * Gravity,
            .z_ms2 = static_cast<float>(raw_z) * Sensitivity * Gravity
        };
    }

private:
    static constexpr uint8_t ExpectedChipId    = 0x6A;
    static constexpr uint8_t AutoIncrementFlag = 0x80;

    static constexpr uint8_t Ctrl1Odr100Hz     = (0x04 << 4);
    static constexpr uint8_t Ctrl1AxesXyz      = (0x07 << 0);
    static constexpr uint8_t Ctrl2BduEnable    = (1 << 7);
    static constexpr uint8_t Ctrl2Fsr2G        = (0x00 << 4);

    Transport& transport_;
    uint8_t dev_addr_;

    bool read_single_reg(Reg reg, uint8_t& val) noexcept {
        return transport_.read(dev_addr_, reg, std::span<uint8_t, 1>{&val, 1});
    }

    bool write_single_reg(Reg reg, uint8_t val) noexcept {
        const uint8_t buf = val;
        return transport_.write(dev_addr_, reg, std::span<const uint8_t, 1>{&buf, 1});
    }
};

} // namespace driver
