#pragma once

// Двоканальний контур E-Stop: імпульсна діагностика ліній, фільтр брязкоту
// й контроль часу дискордансу.

#include <array>
#include <expected>
#include <optional>

#include "safety_hal.hpp"

namespace safety {

enum class LineFault : std::uint8_t {
    ShortToSupply,   // лінія притиснута до шини +24 В
    CrossCircuit,    // канал A зрощений з каналом B
    Discordance      // канали розійшлися довше за t_disc
};

class ChannelMonitor {
public:
    static constexpr Millis kDebounce{8};        // брязкіт срібних контактів
    static constexpr Millis kPulsePeriod{20};    // T_test: 10–50 мс
    static constexpr Micros kPulseWidth{300};    // t_pulse: 100–500 мкс
    static constexpr Micros kPulseGap{200};      // фази T1 і T2 не перекриваються
    static constexpr Millis kDiscrepancy{100};   // t_disc: 50–200 мс

    explicit ChannelMonitor(Hal& hal);

    // true — обидва канали стабільно замкнені; false — контур розірвано
    // або канали розбіглися; помилка — дефект ліній, що залипає.
    [[nodiscard]] std::expected<bool, LineFault> update(Millis dt);

private:
    // Фільтр брязкоту: рівень стає стабільним лише протримавшись kDebounce.
    // Вікно навмисно набагато вужче за t_disc — інакше сам фільтр створював
    // би розбіжність каналів.
    class Debounced {
    public:
        void feed(bool raw, Millis dt);
        [[nodiscard]] bool stable() const noexcept { return stable_; }

    private:
        bool   stable_{};
        bool   candidate_{};
        Millis settled_{};
    };

    void runPulseTest();

    Hal&                       hal_;
    std::array<Debounced, 2>   inputs_{};
    std::optional<LineFault>   fault_{};
    Millis                     pulseTimer_{};
    Millis                     mismatchTimer_{};
    bool                       mismatching_{};
};

}  // namespace safety
