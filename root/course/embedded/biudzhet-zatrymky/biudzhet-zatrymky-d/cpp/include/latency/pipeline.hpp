// pipeline.hpp — тракт як послідовність ланок і арифметика над ним.
//
// Тракт зберігається у Pipeline<N> (фіксована місткість, жодного виділення
// пам'яті), а всі підрахунки працюють над std::span<const Stage>. Завдяки
// цьому однакова функція обслуговує тракт із семи ланок і тракт із
// дванадцяти, і навіть суму двох трактів не треба десь копіювати.
#pragma once

#include <algorithm>
#include <array>
#include <cstddef>
#include <optional>
#include <span>
#include <stdexcept>

#include "latency/stage.hpp"

namespace latency {

struct Summary {
    Ms min{};
    Ms typ{};
    Ms max{};
    Ms jitter{};      // max - min: розмах, який контур бачить як шум
    Ms electronic{};  // typ того, що можна прискорити інженерією
    Ms physical{};    // typ того, що впирається у фізику
};

// Контур оператора замикається двічі: команда туди, картинка назад.
constexpr Summary operator+(const Summary& a, const Summary& b) noexcept {
    return Summary{a.min + b.min,
                   a.typ + b.typ,
                   a.max + b.max,
                   (a.max + b.max) - (a.min + b.min),
                   a.electronic + b.electronic,
                   a.physical + b.physical};
}

constexpr Summary summarize(std::span<const Stage> stages) noexcept {
    Summary s{};
    for (const Stage& st : stages) {
        s.min += st.min;
        s.typ += st.typ;
        s.max += st.max;
        (st.domain == Domain::Electronic ? s.electronic : s.physical) += st.typ;
    }
    s.jitter = s.max - s.min;
    return s;
}

// Найтовща ланка за найгіршим випадком — з неї починають боротьбу за лаг.
constexpr std::optional<Stage> bottleneck(std::span<const Stage> stages) noexcept {
    if (stages.empty()) {
        return std::nullopt;
    }
    const auto it = std::ranges::max_element(stages, {}, &Stage::max);
    return *it;
}

// Частка найтовщої ланки в найгіршому випадку тракту.
constexpr double bottleneck_share(std::span<const Stage> stages) noexcept {
    const auto worst = bottleneck(stages);
    const Ms total = summarize(stages).max;
    if (!worst || !(total > Ms{0})) {
        return 0.0;
    }
    return worst->max / total;
}

// Найбільший часовий квант серед тактових ланок: закон пляшкового горла
// каже оптимізувати саме його, а не мікросекунди DShot. Тракт без тактових
// ланок — не помилка, а окремий випадок, тож відповідь порожня.
constexpr std::optional<Stage> worst_quantum(std::span<const Stage> stages) noexcept {
    std::optional<Stage> worst{};
    for (const Stage& st : stages) {
        if (st.kind != Kind::Periodic) {
            continue;
        }
        if (!worst || st.period > worst->period) {
            worst = st;
        }
    }
    return worst;
}

// --- Динаміка замкненого контуру -------------------------------------------

// Чиста затримка дає лінійно наростальний фазовий зсув: 360° · f · t.
constexpr double phase_shift_deg(Ms delay, double control_hz) noexcept {
    return 360.0 * control_hz * (delay.count() / 1000.0);
}

enum class Pio {
    Safe,     // запас за фазою є
    Watch,    // оператор уже відчуває «гуму» на ручці
    Unstable  // зворотний зв'язок став позитивним: розгойдування
};

constexpr Pio pio_risk(double phase_deg) noexcept {
    if (phase_deg >= 90.0) return Pio::Unstable;
    if (phase_deg >= 45.0) return Pio::Watch;
    return Pio::Safe;
}

constexpr std::string_view to_string(Pio risk) noexcept {
    switch (risk) {
        case Pio::Safe:     return "запас за фазою є";
        case Pio::Watch:    return "ручка «гумова», оператор перекеровує";
        case Pio::Unstable: return "PIO: зворотний зв'язок став позитивним";
    }
    return "?";
}

// Скільки метрів апарат проходить наосліп за час затримки.
constexpr double blind_distance_m(Ms delay, double speed_mps) noexcept {
    return speed_mps * (delay.count() / 1000.0);
}

// --- Тракт ------------------------------------------------------------------

// Легкий погляд на тракт: назва плюс ланки. Саме його беруть звіти,
// тож друкувальний код нічого не знає про місткість Pipeline<N>.
struct Track {
    std::string_view          title{};
    std::span<const Stage>    stages{};

    [[nodiscard]] constexpr Summary summary() const noexcept { return summarize(stages); }
};

template <std::size_t Capacity>
class Pipeline {
public:
    constexpr explicit Pipeline(std::string_view title) noexcept : title_{title} {}

    constexpr Pipeline& add(Stage stage) {
        if (size_ >= Capacity) {
            throw std::length_error{"тракт переповнено: збільш місткість Pipeline"};
        }
        stages_[size_++] = stage;
        return *this;
    }

    [[nodiscard]] constexpr Track track() const noexcept {
        return Track{title_, std::span<const Stage>{stages_.data(), size_}};
    }

    [[nodiscard]] constexpr std::string_view title() const noexcept { return title_; }
    [[nodiscard]] constexpr std::size_t size() const noexcept { return size_; }

private:
    std::string_view            title_;
    std::array<Stage, Capacity> stages_{};
    std::size_t                 size_{0};
};

}  // namespace latency
