#pragma once

#include <array>
#include <chrono>
#include <optional>

#include "faults.hpp"

namespace autopilot::failsafe {

using Millis = std::chrono::milliseconds;

/* Пороги підтвердження, індексовані номером відмови. Нуль означає
 * підтвердження в тому ж такті: відмову приводу й втрату орієнтації
 * фільтрувати немає сенсу, це вже не завада в ефірі. */
struct Config {
    std::array<Millis, kFaultCount> debounce{};
    Millis actionHold{500}; // мінімальний квант між змінами дії

    [[nodiscard]] static Config defaults() noexcept;
};

/* Чиста функція таблиці пріоритетів: підтверджена маска → дія.
 * Без стану й без часу, тому її можна перебрати вичерпно. */
[[nodiscard]] Action decide(const FaultMask& confirmed) noexcept;

class Arbiter {
public:
    explicit Arbiter(Config cfg) noexcept : cfg_(cfg) {}

    // Калібрування сенсорів завершене — з цієї миті таймери мають сенс.
    void preflightDone(Millis now) noexcept;

    // Зняття з охорони: повне скидання, включно з фіксацією дії.
    void disarm() noexcept;

    // Явна команда оператора з пульта. false — виходу немає (Terminate).
    [[nodiscard]] bool operatorAck(Millis now) noexcept;

    // Один такт: сирі прапорці → підтверджена маска → дія автопілота.
    Action update(const FaultMask& raw, Millis now) noexcept;

    [[nodiscard]] const FaultMask& confirmed() const noexcept { return confirmed_; }
    [[nodiscard]] Action action() const noexcept { return action_; }
    [[nodiscard]] bool armed() const noexcept { return armed_; }

private:
    void resetTimers() noexcept;

    Config cfg_;
    // optional замість нуля-сентинела: мітка часу 0 — цілком валідна.
    std::array<std::optional<Millis>, kFaultCount> since_{};
    FaultMask confirmed_{};
    Action action_{Action::None};
    Millis action_since_{0};
    bool armed_{false};
};

} // namespace autopilot::failsafe
