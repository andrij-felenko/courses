#include <array>
#include <cstddef>
#include <optional>

namespace viterbi {

class TracebackSmu {
public:
    constexpr TracebackSmu() noexcept {
        reset();
    }

    constexpr void reset() noexcept {
        t_ = 0;
        metric_.fill(INF);
        metric_[0] = 0;                               // старт відомий — стан 00
        for (auto& row : dec_) {
            row.fill(0);
        }
    }

    // Подати прийняту пару; повертає декодований біт, якщо вікно наповнене.
    [[nodiscard]] constexpr std::optional<int> step(int r0, int r1) noexcept {
        const auto res = acs(metric_, r0, r1);
        dec_[t_ % D] = res.decisions;                 // нову колонку — одразу в кільце
        metric_ = res.metrics;
        t_++;

        if (t_ < D) return std::nullopt;              // вікно ще не повне — warm-up

        std::size_t s = best_state(metric_);          // старт простеження — найкращий стан
        for (std::size_t k = 0; k < D - 1; ++k) {     // крок назад крізь вікно
            const std::size_t col = (t_ - 1 - k) % D;
            s = ((s & LOW) << 1) | dec_[col][s];      // відновити попередника з біта рішення
        }
        return static_cast<int>(s >> (NU - 1));       // найдавніший вхідний біт вікна
    }

    [[nodiscard]] constexpr std::size_t ticks() const noexcept { return t_; }

private:
    std::array<std::array<unsigned, S>, D> dec_{};    // кільце з D колонок рішень
    std::array<int, S> metric_{};
    std::size_t t_{0};                                // скільки тактів опрацьовано
};

} // namespace viterbi
