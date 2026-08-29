#pragma once

// Кнопка мертвої руки: кінематика 3-позиційного перемикача за IEC 60947-5-8
// і циклічний контроль пильності з ескалацією тривоги.

#include <expected>

#include "safety_hal.hpp"

namespace safety {

enum class Grip : std::uint8_t {
    Released,   // Позиція 1
    Enabled,    // Позиція 2 — рух дозволено
    Panic,      // Позиція 3 або блокування, зведене нею
    Dozed       // пильність не підтверджено, дозвіл знято до відпускання
};

// Єдиний дефект, що залипає: контакти дозволу розійшлися.
enum class EnableFault : std::uint8_t { ContactDiscordance };

struct Indicators {
    bool lamp{};
    bool buzzer{};
};

class EnablingDevice {
public:
    static constexpr Millis kSplitLimit{100};        // розбіжність контактів
    static constexpr Millis kVigilanceCycle{45000};  // T_cycle: 30–60 с
    static constexpr Millis kVigilanceWarn{2500};    // T_warn: світлова фаза
    static constexpr Millis kVigilanceAlarm{2500};   // T_alarm: звукова фаза

    explicit EnablingDevice(Hal& hal) : hal_{hal} {}

    [[nodiscard]] std::expected<Grip, EnableFault> update(Millis dt);

    [[nodiscard]] Indicators indicators() const noexcept { return indicators_; }
    [[nodiscard]] bool ready() const noexcept { return grip_ == Grip::Enabled && !split_; }

private:
    void updateVigilance(Millis dt);

    Hal&       hal_;
    Grip       grip_{Grip::Released};
    bool       panicLatch_{};   // Позиція 3 блокує дозвіл до повного відпускання
    bool       split_{};        // канали A і B не збігаються просто зараз
    bool       faulted_{};
    bool       ackPrev_{};
    Millis     splitTimer_{};
    Millis     idleTimer_{};
    Indicators indicators_{};
};

}  // namespace safety
