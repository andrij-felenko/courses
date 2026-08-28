#include <cstdint>
#include <cmath>
#include <concepts>
#include <span>
#include <expected>
#include <optional>

enum class IrStatus : uint8_t {
    Ok = 0,
    BusError,
    PecMismatch,
    SensorOverflow,
    InvalidParameter
};

// Концепт для апаратно-незалежного транспорту шини I2C/SMBus (RAII / Dependency Injection)
template <typename T>
concept I2cBusTransport = requires(T bus, uint8_t addr, std::span<const uint8_t> tx, std::span<uint8_t> rx) {
    { bus.write(addr, tx) } -> std::same_as<bool>;
    { bus.read(addr, rx) }  -> std::same_as<bool>;
};

template <I2cBusTransport Transport>
class IrThermometer {
public:
    static constexpr uint8_t DEFAULT_I2C_ADDR = 0x5A;
    static constexpr uint8_t CMD_RAM_TA       = 0x06;
    static constexpr uint8_t CMD_RAM_TOBJ1    = 0x07;

    struct Config {
        uint8_t address{DEFAULT_I2C_ADDR};
        float emissivity{0.95f};
        std::optional<float> custom_reflected_temp_c{std::nullopt};
    };

    explicit constexpr IrThermometer(Transport& bus, Config cfg = {})
        : bus_(bus), config_(cfg) {}

    void set_emissivity(float eps) noexcept {
        config_.emissivity = std::clamp(eps, 0.01f, 1.0f);
    }

    void set_reflected_temperature(std::optional<float> temp_c) noexcept {
        config_.custom_reflected_temp_c = temp_c;
    }

    // Зчитування температури кристала сенсора (холодних спаїв)
    [[nodiscard]] std::expected<float, IrStatus> read_ambient_temperature() const {
        auto raw_opt = read_register(CMD_RAM_TA);
        if (!raw_opt) {
            return std::unexpected(raw_opt.error());
        }
        return (*raw_opt * 0.02f) - 273.15f;
    }

    // Зчитування істинної температури об'єкта з повною радіаційною корекцією
    [[nodiscard]] std::expected<float, IrStatus> read_object_temperature() const {
        auto raw_opt = read_register(CMD_RAM_TOBJ1);
        if (!raw_opt) {
            return std::unexpected(raw_opt.error());
        }

        const float t_rad_k = static_cast<float>(*raw_opt) * 0.02f;

        if (config_.emissivity >= 0.999f && !config_.custom_reflected_temp_c.has_value()) {
            return t_rad_k - 273.15f;
        }

        float t_amb_k = 298.15f; // 25 °C за замовчуванням
        if (config_.custom_reflected_temp_c.has_value()) {
            t_amb_k = *config_.custom_reflected_temp_c + 273.15f;
        } else {
            auto amb_res = read_ambient_temperature();
            if (amb_res) {
                t_amb_k = *amb_res + 273.15f;
            }
        }

        const double eps = static_cast<double>(config_.emissivity);
        const double t_rad_4 = std::pow(static_cast<double>(t_rad_k), 4.0);
        const double t_amb_4 = std::pow(static_cast<double>(t_amb_k), 4.0);

        const double num = t_rad_4 - (1.0 - eps) * t_amb_4;
        if (num <= 0.0) {
            return std::unexpected(IrStatus::SensorOverflow);
        }

        const double t_obj_k = std::pow(num / eps, 0.25);
        return static_cast<float>(t_obj_k - 273.15);
    }

private:
    Transport& bus_;
    Config config_;

    static constexpr uint8_t crc8_step(uint8_t crc, uint8_t byte) noexcept {
        crc ^= byte;
        for (uint8_t i = 0; i < 8; ++i) {
            crc = (crc & 0x80) ? static_cast<uint8_t>((crc << 1) ^ 0x07) : static_cast<uint8_t>(crc << 1);
        }
        return crc;
    }

    [[nodiscard]] std::expected<uint16_t, IrStatus> read_register(uint8_t reg_cmd) const {
        const uint8_t tx[1] = { reg_cmd };
        uint8_t rx[3] = { 0, 0, 0 }; // LSB, MSB, PEC

        if (!bus_.write(config_.address, tx)) {
            return std::unexpected(IrStatus::BusError);
        }
        if (!bus_.read(config_.address, rx)) {
            return std::unexpected(IrStatus::BusError);
        }

        uint8_t calc_pec = 0;
        calc_pec = crc8_step(calc_pec, static_cast<uint8_t>(config_.address << 1));
        calc_pec = crc8_step(calc_pec, reg_cmd);
        calc_pec = crc8_step(calc_pec, static_cast<uint8_t>((config_.address << 1) | 1));
        calc_pec = crc8_step(calc_pec, rx[0]);
        calc_pec = crc8_step(calc_pec, rx[1]);

        if (calc_pec != rx[2]) {
            return std::unexpected(IrStatus::PecMismatch);
        }

        const uint16_t raw = static_cast<uint16_t>(rx[0] | (static_cast<uint16_t>(rx[1]) << 8));
        if (raw & 0x8000) {
            return std::unexpected(IrStatus::SensorOverflow);
        }

        return raw;
    }
};
