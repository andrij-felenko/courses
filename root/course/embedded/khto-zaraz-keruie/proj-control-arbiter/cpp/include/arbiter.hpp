#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <string_view>

namespace flight::control {

/* Час — від старту борту, у мікросекундах. Тип із <chrono> замість голого
   uint64_t: додати сюди мілісекунди чи порівняти з таймаутом не переплутавши
   одиниці тепер неможливо — це ловить компілятор. */
using Timestamp = std::chrono::microseconds;

enum class Axis : std::size_t { Roll = 0, Pitch, Yaw, Thrust };
inline constexpr std::size_t kAxisCount = 4;

/* Джерела в порядку спадання авторитету: значення і є пріоритет. */
enum class SourceId : std::size_t { Failsafe = 0, RcPilot, Offboard, GcsMission };
inline constexpr std::size_t kSourceCount = 4;

[[nodiscard]] constexpr std::string_view name(SourceId id) noexcept {
    switch (id) {
        case SourceId::Failsafe:   return "FAILSAFE";
        case SourceId::RcPilot:    return "RC";
        case SourceId::Offboard:   return "OFFBOARD";
        case SourceId::GcsMission: return "GCS";
    }
    return "?";
}

/* Результат прийому кадру. Замість -1 з errno — перелік із власним значенням
   на кожну відмову; [[nodiscard]] не дає мовчки його загубити. */
enum class SubmitResult { Ok, UnknownSource, NotFinite, OutOfRange, StaleFrame };

[[nodiscard]] constexpr std::string_view name(SubmitResult r) noexcept {
    switch (r) {
        case SubmitResult::Ok:            return "прийнято";
        case SubmitResult::UnknownSource: return "невідоме джерело";
        case SubmitResult::NotFinite:     return "NaN у каналі";
        case SubmitResult::OutOfRange:    return "поза межами апарата";
        case SubmitResult::StaleFrame:    return "кадр із минулого";
    }
    return "?";
}

/* Roll/Pitch — кут нахилу (рад), Yaw — кутова швидкість (рад/с), Thrust —
   нормована тяга [0..1]. Повний хід кутової ручки — 1.0. */
struct Setpoint {
    Timestamp stamp{0};
    std::array<float, kAxisCount> ch{};

    [[nodiscard]] constexpr float& operator[](Axis a) noexcept {
        return ch[static_cast<std::size_t>(a)];
    }
    [[nodiscard]] constexpr float operator[](Axis a) const noexcept {
        return ch[static_cast<std::size_t>(a)];
    }
};

struct SourceConfig {
    Timestamp timeout{std::chrono::milliseconds{500}};
    float stick_deadband{0.08f};       // поріг входу в ручний пріоритет
    float stick_deadband_exit{0.05f};  // поріг виходу — гістерезис проти тремтіння
    std::array<float, kAxisCount> max_slew_rate{6.0f, 6.0f, 10.0f, 3.0f};
};

class ControlArbiter {
public:
    /* Рішення такту одним значенням: жодних вихідних параметрів і жодного
       вартового SourceId::None — «джерела немає» виражає порожній optional. */
    struct Decision {
        std::optional<SourceId> source{};
        Setpoint output{};
        bool valid{false};        // false — керувати нічим, іде аварійний профіль
        float deflection{0.0f};   // норма Чебишова по стіках, у чорну скриньку
    };

    ControlArbiter() noexcept;

    [[nodiscard]] SubmitResult submit(SourceId id, const Setpoint& sp, Timestamp now) noexcept;
    void raise_failsafe(float descent_thrust, Timestamp now) noexcept;
    void clear_failsafe() noexcept;

    /* Один виклик на такт польотного циклу. */
    [[nodiscard]] Decision evaluate(Timestamp now) noexcept;

    [[nodiscard]] bool is_live(SourceId id) const noexcept;
    [[nodiscard]] std::optional<SourceId> active_source() const noexcept { return active_; }
    [[nodiscard]] std::uint32_t switch_count() const noexcept { return switches_; }
    [[nodiscard]] std::uint32_t reject_count() const noexcept { return rejects_; }

private:
    struct Slot {
        Setpoint sp{};
        Timestamp heartbeat{0};
        SourceConfig config{};
        bool has_data{false};
        bool timed_out{true};
    };

    [[nodiscard]] Slot& slot(SourceId id) noexcept {
        return slots_[static_cast<std::size_t>(id)];
    }
    [[nodiscard]] const Slot& slot(SourceId id) const noexcept {
        return slots_[static_cast<std::size_t>(id)];
    }

    void update_watchdog(Timestamp now) noexcept;
    [[nodiscard]] std::optional<SourceId> select() noexcept;

    std::array<Slot, kSourceCount> slots_{};
    std::optional<SourceId> active_{};
    Setpoint output_{};
    Timestamp last_eval_{0};
    bool output_valid_{false};
    bool failsafe_latched_{false};
    bool override_latched_{false};
    float deflection_{0.0f};
    std::uint32_t switches_{0};
    std::uint32_t rejects_{0};
};

}  // namespace flight::control
