#include <cstdint>
#include <expected>
#include <chrono>
#include "stm32f4xx.h"

template <typename BusInterface, typename PowerController>
class ResilientSensorDriver {
public:
    struct ShadowConfig {
        uint8_t ctrl_reg{0x57};
        uint8_t config_reg{0x08};
    };

    ResilientSensorDriver(BusInterface bus, PowerController power, uint8_t dev_addr, uint8_t expected_id) noexcept
        : bus_{bus}, power_{power}, dev_addr_{dev_addr}, expected_id_{expected_id} {}

    [[nodiscard]] std::expected<void, BusError> initialize() noexcept {
        auto check_id = [this]() -> std::expected<void, BusError> {
            auto id_res = bus_.read_byte(dev_addr_, 0x0F /* WHO_AM_I */);
            if (!id_res.has_value() || *id_res != expected_id_) {
                return std::unexpected(BusError::Nack);
            }
            return {};
        };

        if (!check_id().has_value()) {
            return recover_and_reconfigure();
        }

        // Запис конфігурації
        auto res1 = bus_.write_byte(dev_addr_, 0x20, shadow_cfg_.ctrl_reg);
        if (!res1.has_value()) return recover_and_reconfigure();

        auto res2 = bus_.write_byte(dev_addr_, 0x21, shadow_cfg_.config_reg);
        if (!res2.has_value()) return recover_and_reconfigure();

        consecutive_faults_ = 0;
        return {};
    }

    [[nodiscard]] std::expected<int16_t, BusError> read_measurement(uint8_t lsb_reg, uint8_t msb_reg) noexcept {
        auto lsb = bus_.read_byte(dev_addr_, lsb_reg);
        if (!lsb) {
            auto rec = recover_and_reconfigure();
            if (!rec) return std::unexpected(rec.error());
            return std::unexpected(lsb.error());
        }

        auto msb = bus_.read_byte(dev_addr_, msb_reg);
        if (!msb) {
            auto rec = recover_and_reconfigure();
            if (!rec) return std::unexpected(rec.error());
            return std::unexpected(msb.error());
        }

        consecutive_faults_ = 0;
        return static_cast<int16_t>((*msb << 8) | *lsb);
    }

private:
    BusInterface bus_;
    PowerController power_;
    uint8_t dev_addr_;
    uint8_t expected_id_;
    ShadowConfig shadow_cfg_{};
    uint8_t consecutive_faults_{0};

    [[nodiscard]] std::expected<void, BusError> recover_and_reconfigure() noexcept {
        ++consecutive_faults_;

        if (consecutive_faults_ == 1) {
            // Tier 1: Відновлення шини + Soft Reset
            bus_.recover_bus();
            bus_.write_byte(dev_addr_, 0x25, 0xB6);
        } else if (consecutive_faults_ == 2) {
            // Tier 2: Апаратний імпульс nRESET
            power_.pulse_reset_pin();
        } else {
            // Tier 3: Повний Power-Cycle MOSFET
            power_.execute_power_cycle();
            consecutive_faults_ = 0;
        }

        // Перевірка відновлення працездатності
        auto id_check = bus_.read_byte(dev_addr_, 0x0F);
        if (id_check && *id_check == expected_id_) {
            // Відновлення тіньових регістрів
            bus_.write_byte(dev_addr_, 0x20, shadow_cfg_.ctrl_reg);
            bus_.write_byte(dev_addr_, 0x21, shadow_cfg_.config_reg);
            consecutive_faults_ = 0;
            return {};
        }

        return std::unexpected(BusError::BusStuck);
    }
};
