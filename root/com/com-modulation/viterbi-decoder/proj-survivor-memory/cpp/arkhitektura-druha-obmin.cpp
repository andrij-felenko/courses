#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace viterbi {

class RegisterExchangeSmu {
public:
    constexpr RegisterExchangeSmu() noexcept {
        reset();
    }

    constexpr void reset() noexcept {
        t_ = 0;
        metric_.fill(INF);
        metric_[0] = 0;
        reg_.fill(0);
    }

    // Подати прийняту пару; повертає декодований біт без зворотного проходу.
    [[nodiscard]] constexpr std::optional<int> step(int r0, int r1) noexcept {
        std::array<int, S> nm{};
        std::array<uint32_t, S> nreg{};
        nm.fill(INF);
        nreg.fill(0);

        for (std::size_t s = 0; s < S; ++s) {
            if (metric_[s] == INF) continue;
            for (int u = 0; u < 2; ++u) {
                const std::size_t ns = static_cast<std::size_t>(NXT[s][u]);
                const int cand = metric_[s] + hamming_distance(OUT[s][u], r0, r1);
                if (cand < nm[ns]) {
                    nm[ns] = cand;
                    const uint32_t unew = static_cast<uint32_t>(ns >> (NU - 1)); // вхідний біт ребра
                    nreg[ns] = ((reg_[s] << 1) | unew) & ((1u << D) - 1);        // копія + зсув
                }
            }
        }

        metric_ = nm;
        reg_ = nreg;                                  // УСЯ пам'ять оновлюється щотакту
        t_++;

        if (t_ < D) return std::nullopt;

        const std::size_t best = best_state(metric_);
        return static_cast<int>((reg_[best] >> (D - 1)) & 1u); // найстарший біт — миттєво
    }

    [[nodiscard]] constexpr std::size_t ticks() const noexcept { return t_; }

private:
    std::array<uint32_t, S> reg_{};                   // D-бітний префікс шляху на кожен стан
    std::array<int, S> metric_{};
    std::size_t t_{0};
};

} // namespace viterbi
