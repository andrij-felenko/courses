// Демонстрація фільтра впевненості: калібрування логітів, траса одного треку
// такт за тактом, пул треків із таймаутом і поведінка на переповненні пулу.
// Збірка: c++ -std=c++23 -O2 -Wall -Wextra main.cpp -o decision_filter

#include "track_pool.hpp"

#include <array>
#include <format>
#include <iostream>
#include <string>

namespace {

constexpr Millis kTick{50};

// Пороги з розбору в статті: alpha = 0.75, H_on = 0.70, H_off = 0.35,
// утримання 200 мс, голосування 3 з 5.
constexpr DecisionConfidenceFilter::Config kFilterConfig{
    .temperature = 2.0f,
    .alpha = 0.75f,
    .thresh_on = 0.70f,
    .thresh_off = 0.35f,
    .min_hold = Millis{200},
    .window_size = 5,
    .min_votes = 3,
    .fail_safe_start = false,
};

[[nodiscard]] std::string windowBits(std::uint32_t window, std::uint8_t bits) {
    return std::format("{:0{}b}", window, static_cast<int>(bits));
}

void demoCalibration() {
    struct Sample {
        float target;
        float background;
        std::string_view note;
    };
    constexpr std::array samples{
        Sample{6.0f, -1.0f, "впевнена детекція"},
        Sample{0.4f, 0.1f, "межа видимості"},
        Sample{-3.0f, 2.5f, "чистий фон"},
        Sample{40.0f, -40.0f, "насичений логіт: без зсуву на максимум був би +inf"},
    };

    std::cout << "=== Температурне калібрування (T = 2.0) ===\n";
    for (const auto& [target, background, note] : samples) {
        const float raw = DecisionConfidenceFilter::calibrate(target, background, 1.0f);
        const float cal = DecisionConfidenceFilter::calibrate(target, background,
                                                              kFilterConfig.temperature);
        std::cout << std::format("z = ({:+6.1f}, {:+6.1f})  ->  P(T=1) = {:.4f}   P(T=2) = {:.4f}  {}\n",
                                 target, background, raw, cal, note);
    }
    std::cout << '\n';
}

// Траса: одиночний спалах шуму, потім справжня перешкода з провалом детекції.
void demoTrace() {
    constexpr std::array probs{
        0.05f, 0.95f, 0.04f, 0.85f, 0.90f, 0.88f, 0.10f, 0.92f, 0.05f, 0.02f,
    };

    auto made = DecisionConfidenceFilter::make(kFilterConfig);
    if (!made) {
        std::cerr << std::format("конфігурація фільтра непридатна: {}\n", describe(made.error()));
        return;
    }
    DecisionConfidenceFilter filter = *made;

    std::cout << "=== Траса одного треку ===\n";
    std::cout << " k | час, мс | P[k]  | S[k]  | вікно | голоси | вихід\n";

    for (std::size_t k = 0; k < probs.size(); ++k) {
        const Millis now = kTick * static_cast<int>(k);
        const bool active = filter.update(probs[k], now);

        std::cout << std::format("{:2} | {:7} | {:.3f} | {:.3f} | {} | {} з {}  | {}\n",
                                 k + 1, now.count(), probs[k], filter.score(),
                                 windowBits(filter.window(), kFilterConfig.window_size),
                                 filter.votes(), static_cast<int>(kFilterConfig.window_size),
                                 active ? "ТРИВОГА" : "норма");
    }
    std::cout << '\n';
}

// Кадр супроводу: від'ємне значення означає, що трекер об'єкта в кадрі не побачив.
struct TrackScript {
    int id;
    std::string_view label;
    std::array<float, 12> probs;
};

void demoPool() {
    constexpr std::array scripts{
        TrackScript{7, "пішохід",
                    {0.10f, 0.80f, 0.86f, 0.91f, 0.88f, 0.93f,
                     0.10f, 0.90f, 0.87f, 0.05f, 0.03f, 0.02f}},
        TrackScript{11, "стовп на узбіччі",
                    {0.90f, 0.92f, 0.88f, -1.0f, -1.0f, -1.0f,
                     -1.0f, -1.0f, -1.0f, -1.0f, -1.0f, -1.0f}},
        TrackScript{42, "відблиск на асфальті",
                    {0.02f, 0.97f, 0.03f, 0.01f, 0.95f, 0.04f,
                     0.02f, 0.01f, 0.03f, 0.02f, 0.01f, 0.00f}},
    };
    constexpr Millis kTrackTimeout{300};

    auto made = TrackerFilterPool<>::make(kFilterConfig);
    if (!made) {
        std::cerr << std::format("пул не створено: {}\n", describe(made.error()));
        return;
    }
    auto& pool = *made;

    std::cout << "=== Пул треків (таймаут треку 300 мс) ===\n";
    for (std::size_t k = 0; k < scripts.front().probs.size(); ++k) {
        const Millis now = kTick * static_cast<int>(k);

        for (const auto& script : scripts) {
            const float p = script.probs[k];
            if (p < 0.0f) {
                continue;  // Об'єкта в цьому кадрі немає — слот доживає до таймауту.
            }
            auto slot = pool.track(script.id, now);
            if (!slot) {
                std::cerr << std::format("трек {} втрачено: {}\n", script.id,
                                         describe(slot.error()));
                continue;
            }
            slot->get().update(p, now);
        }

        const std::size_t dropped = pool.sweep(kTrackTimeout, now);

        std::string line = std::format("t = {:4} мс | слотів {} | команда: {:<10} |",
                                       now.count(), pool.size(),
                                       pool.anyActive() ? "ГАЛЬМУВАТИ" : "рух");
        pool.forEach([&line](int id, const DecisionConfidenceFilter& filter) {
            line += std::format(" {}:{}({:.2f})", id, filter.isActive() ? "!" : "-",
                                filter.score());
        });
        if (dropped > 0) {
            line += std::format("  [прибрано за таймаутом: {}]", dropped);
        }
        std::cout << line << '\n';
    }

    for (const auto& script : scripts) {
        auto slot = pool.find(script.id);
        const std::string_view verdict =
            !slot ? "прибрано за таймаутом" : (slot->get().isActive() ? "тривога" : "норма");
        std::cout << std::format("трек {:2} ({}): {}\n", script.id, script.label, verdict);
    }
    std::cout << '\n';
}

// Пул скінченний, і переповнення — не гіпотеза: у щільному потоці трекер
// легко видає більше рамок, ніж є слотів.
void demoPoolExhaustion() {
    auto made = TrackerFilterPool<>::make(kFilterConfig);
    if (!made) {
        std::cerr << std::format("пул не створено: {}\n", describe(made.error()));
        return;
    }
    auto& pool = *made;

    std::cout << "=== Переповнення пулу ===\n";
    for (int id = 100; id < 100 + static_cast<int>(pool.capacity()); ++id) {
        if (!pool.track(id, Millis{0})) {
            std::cout << std::format("несподівана відмова на треку {}\n", id);
            return;
        }
    }
    std::cout << std::format("зайнято слотів: {} з {}\n", pool.size(), pool.capacity());

    if (auto slot = pool.track(999, Millis{0}); !slot) {
        std::cout << std::format("трек 999 відхилено — {}\n", describe(slot.error()));
    }

    pool.release(100);
    if (pool.track(999, Millis{0})) {
        std::cout << "після звільнення слоту трек 999 прийнято\n";
    }
    std::cout << '\n';
}

}  // namespace

int main() {
    if (auto ok = DecisionConfidenceFilter::validate(kFilterConfig); !ok) {
        std::cerr << std::format("конфігурація не пройшла перевірку: {}\n", describe(ok.error()));
        return 1;
    }
    demoCalibration();
    demoTrace();
    demoPool();
    demoPoolExhaustion();
    return 0;
}
