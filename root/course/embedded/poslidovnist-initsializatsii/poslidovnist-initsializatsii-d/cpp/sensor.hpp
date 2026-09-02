#pragma once

#include <chrono>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

#include "platform.hpp"

namespace bringup {

// --- Регістрова карта навчального MEMS-давача -------------------------------
// Карта замкнена сама на себе: рівно її реалізує модель чипа в platform_sim.cpp.
namespace reg {
inline constexpr std::uint8_t ResetCtrl = 0x06;  // R/W, біт 7 самоочисний
inline constexpr std::uint8_t Status    = 0x07;  // RO
inline constexpr std::uint8_t WhoAmI    = 0x0F;  // RO
inline constexpr std::uint8_t IntCfg    = 0x10;  // крок 1
inline constexpr std::uint8_t Range     = 0x11;  // крок 2
inline constexpr std::uint8_t Filter    = 0x12;  // крок 3
inline constexpr std::uint8_t IntEnable = 0x13;  // крок 4
inline constexpr std::uint8_t Power     = 0x14;  // крок 5
}  // namespace reg

namespace bits {
inline constexpr std::uint8_t SwReset     = 1u << 7;
inline constexpr std::uint8_t StatusReady = 1u << 0;
inline constexpr std::uint8_t StatusDrdy  = 1u << 7;
inline constexpr std::uint8_t FilterReady = 1u << 7;  // RO всередині конфігураційного
}  // namespace bits

inline constexpr std::uint8_t WhoAmIValue = 0x6C;
inline constexpr std::uint8_t PowerModeMask = 0x03;
inline constexpr std::uint8_t PowerStandby = 0x00;
inline constexpr std::uint8_t PowerNormal = 0x01;
inline constexpr auto SettlingTime = std::chrono::milliseconds{25};

enum class InitError { Bus, Timeout, WrongId, Verify };
std::string_view to_string(InitError error);

enum class State { Uninitialized, Ready, Fault };

// Одне поле конфігурації разом із маскою значущих (R/W) розрядів.
struct RegField {
    std::uint8_t reg;
    std::uint8_t value;
    std::uint8_t care;
};

// Помилка несе ще й регістр, на якому все зламалося: без цього причину
// невдалої верифікації в полі не знайти.
struct Fault {
    InitError error;
    std::uint8_t reg{0};
};

// Ручне розблокування шини: тактування -> NRST -> перезапуск живлення.
void recover_bus(platform::PowerRail& rail, std::uint8_t dev);

class Sensor {
public:
    Sensor(platform::I2cBus& bus, platform::PowerRail& rail, std::uint8_t addr,
           std::string_view name, bool critical) noexcept;

    std::expected<void, Fault> bring_up();
    [[nodiscard]] std::expected<bool, Fault> data_ready();

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] std::string_view name() const noexcept { return name_; }
    [[nodiscard]] std::uint8_t address() const noexcept { return addr_; }
    [[nodiscard]] bool critical() const noexcept { return critical_; }
    [[nodiscard]] unsigned attempts() const noexcept { return attempts_; }

private:
    std::expected<void, Fault> software_reset();
    std::expected<void, Fault> check_id();
    std::expected<void, Fault> write_verified(const RegField& field);
    std::expected<void, Fault> write_sequence(std::span<const RegField> fields);
    std::expected<void, Fault> apply_config();
    std::expected<void, Fault> attempt();
    void rollback() noexcept;

    platform::I2cBus& bus_;
    platform::PowerRail& rail_;
    std::uint8_t addr_;
    std::string_view name_;
    bool critical_;
    State state_{State::Uninitialized};
    unsigned attempts_{0};
};

}  // namespace bringup
