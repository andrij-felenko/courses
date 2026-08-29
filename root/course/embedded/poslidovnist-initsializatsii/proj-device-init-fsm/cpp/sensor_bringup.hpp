#pragma once

#include "i2c_bus.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <string_view>

namespace bringup {

using Millis = std::chrono::milliseconds;

// Регістри гіпотетичного MEMS-давача.
namespace reg {
inline constexpr std::uint8_t Address = 0x68;
inline constexpr std::uint8_t ChipId = 0x00;
inline constexpr std::uint8_t ResetCtrl = 0x10;
inline constexpr std::uint8_t RangeCtrl = 0x18;
inline constexpr std::uint8_t OdrFilter = 0x19;
inline constexpr std::uint8_t PwrMode = 0x1A;
}  // namespace reg

namespace bit {
inline constexpr std::uint8_t SwReset = 1U << 7;
inline constexpr std::uint8_t DeviceReady = 1U << 0;
inline constexpr std::uint8_t DataReady = 1U << 7;  // RO-статус усередині OdrFilter
}  // namespace bit

inline constexpr std::uint8_t kExpectedChipId = 0xEA;
inline constexpr std::uint8_t kPwrActive = 0x01;

// Часові параметри bring-up. std::chrono не дає переплутати мілісекунди
// з тактами, а 64-бітне представлення знімає питання переповнення лічильника,
// яке в C-версії доводилося тримати в голові.
inline constexpr Millis kPorBoot{25};
inline constexpr Millis kResetWait{10};
inline constexpr Millis kPollTimeout{100};
inline constexpr Millis kAnalogSettle{15};
inline constexpr Millis kBaseBackoff{50};
inline constexpr unsigned kMaxRetries = 3;

enum class State : std::uint8_t {
    PowerOnDelay,
    SendReset,
    PollReady,
    VerifyChipId,
    WriteConfig,
    ReadbackVerify,
    Activate,
    SettlingDelay,
    Ready,
    RetryBackoff,
    FaultSafe
};

std::string_view to_string(State state) noexcept;

// mask — значущі біти регістра: усе поза нею (RO-статуси, зарезервовані
// розряди) під час Read-Back ігнорується.
struct RegConfig {
    std::uint8_t reg;
    std::uint8_t value;
    std::uint8_t mask;
};

// Діапазон ±4g (біти 0..3) та ODR 100 Гц + DLPF 40 Гц (біт 7 — статус DRDY).
inline constexpr std::array<RegConfig, 2> kDefaultConfig{{
    {reg::RangeCtrl, 0x02, 0x0F},
    {reg::OdrFilter, 0x34, 0x7F},
}};

// Неблокуючий автомат запуску давача. Час не читає сам, а дістає ззовні —
// так той самий екземпляр однаково крокує від SysTick і від віртуального
// годинника стенда.
class SensorBringUp {
public:
    SensorBringUp(I2cBus& bus, Millis now,
                  std::span<const RegConfig> config = kDefaultConfig) noexcept;

    // Один крок диспетчера: жодного очікування всередині.
    void step(Millis now);

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] bool ready() const noexcept { return state_ == State::Ready; }
    [[nodiscard]] unsigned retries() const noexcept { return retries_; }

    // Порожньо, доки автомат не впав у безпечний стан.
    [[nodiscard]] std::optional<std::string_view> fault() const noexcept { return fault_; }

private:
    void enter(State state, Millis now) noexcept;
    void retry_or_fail(std::string_view reason, Millis now);
    [[nodiscard]] bool elapsed(Millis now, Millis span) const noexcept;

    I2cBus& bus_;
    std::span<const RegConfig> config_;
    State state_{State::PowerOnDelay};
    Millis entered_{0};
    Millis backoff_{0};
    std::size_t config_idx_{0};
    unsigned retries_{0};
    std::optional<std::string_view> fault_{};
};

}  // namespace bringup
