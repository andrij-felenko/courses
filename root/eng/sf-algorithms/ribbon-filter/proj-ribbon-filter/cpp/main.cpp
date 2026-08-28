#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <bit>
#include <optional>
#include <stdexcept>
#include <iostream>

template <std::size_t Width = 64, std::size_t OverheadPercent = 5>
class RibbonFilter {
public:
    RibbonFilter() = default;

    /* Конструктор, що ініціалізує та будує фільтр за набором ключів */
    explicit RibbonFilter(std::span<const std::uint64_t> keys) {
        if (!build(keys)) {
            throw std::runtime_error("Не вдалося розв'язати лінійну систему стрічкового фільтра");
        }
    }

    /* Побудова фільтра за наданими ключами */
    bool build(std::span<const std::uint64_t> keys) {
        if (keys.empty()) return false;

        num_keys_ = keys.size();
        num_slots_ = (num_keys_ * (100 + OverheadPercent)) / 100;
        if (num_slots_ < Width) num_slots_ = Width;

        slots_.assign(num_slots_, 0);
        std::vector<PivotRow> pivots(num_slots_);

        constexpr std::size_t max_retries = 10;
        for (std::size_t retry = 0; retry < max_retries; ++retry) {
            std::uint64_t candidate_seed = 0x12345678ULL + retry * 0x9e3779b9ULL;
            std::fill(pivots.begin(), pivots.end(), PivotRow{});
            bool success = true;

            /* Прямий хід: інкрементна гаусова редукція */
            for (std::uint64_t key : keys) {
                auto [start_pos, mask, target] = compute_params(key, candidate_seed, num_slots_);
                std::size_t col = start_pos;

                while (mask != 0) {
                    int offset = std::countr_zero(mask);
                    col += static_cast<std::size_t>(offset);
                    mask >>= offset;

                    if (col >= num_slots_) {
                        success = false;
                        break;
                    }

                    if (!pivots[col].occupied) {
                        pivots[col] = { mask, target, true };
                        break;
                    }

                    mask ^= pivots[col].mask;
                    target ^= pivots[col].target;
                }

                if (mask == 0 && target != 0) {
                    success = false;
                    break;
                }
            }

            if (success) {
                /* Зворотний хід: зворотна підстановка значень */
                std::fill(slots_.begin(), slots_.end(), static_cast<std::uint8_t>(0));
                for (std::size_t i = num_slots_; i-- > 0;) {
                    if (pivots[i].occupied) {
                        std::uint8_t accum = 0;
                        std::uint64_t mask = pivots[i].mask;

                        for (std::size_t bit = 1; bit < Width && (i + bit) < num_slots_; ++bit) {
                            if ((mask >> bit) & 1ULL) {
                                accum ^= slots_[i + bit];
                            }
                        }
                        slots_[i] = pivots[i].target ^ accum;
                    }
                }

                seed_ = candidate_seed;
                return true;
            }
        }

        slots_.clear();
        return false;
    }

    /* Перевірка належності ключа у множині */
    [[nodiscard]] bool contains(std::uint64_t key) const noexcept {
        if (slots_.empty()) return false;

        auto [start_pos, mask, expected_target] = compute_params(key, seed_, num_slots_);
        std::uint8_t result = 0;

        for (std::size_t bit = 0; bit < Width && (start_pos + bit) < num_slots_; ++bit) {
            if ((mask >> bit) & 1ULL) {
                result ^= slots_[start_pos + bit];
            }
        }

        return result == expected_target;
    }

    [[nodiscard]] std::size_t size_in_bytes() const noexcept {
        return slots_.size() * sizeof(std::uint8_t);
    }

    [[nodiscard]] std::size_t slot_count() const noexcept { return num_slots_; }
    [[nodiscard]] std::size_t key_count() const noexcept { return num_keys_; }

private:
    struct PivotRow {
        std::uint64_t mask{0};
        std::uint8_t target{0};
        bool occupied{false};
    };

    struct KeyParams {
        std::size_t start_pos;
        std::uint64_t mask;
        std::uint8_t target;
    };

    static inline std::uint64_t splitmix64(std::uint64_t x, std::uint64_t seed) noexcept {
        std::uint64_t z = x + seed + 0x9e3779b97f4a7c15ULL;
        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
        z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
        return z ^ (z >> 31);
    }

    static inline KeyParams compute_params(std::uint64_t key, std::uint64_t seed, std::size_t num_slots) noexcept {
        std::uint64_t h1 = splitmix64(key, seed);
        std::uint64_t h2 = splitmix64(key, seed ^ 0x517cc1b727220a95ULL);

        std::size_t max_start = (num_slots >= Width) ? (num_slots - Width) : 0;
        std::size_t start = static_cast<std::size_t>((static_cast<unsigned __int128>(h1) * (max_start + 1)) >> 64);

        std::uint64_t mask = h2 ? h2 : 1ULL;
        std::uint8_t target = static_cast<std::uint8_t>((h1 >> 32) ^ (h2 >> 32));
        if (target == 0) target = 1;

        return { start, mask, target };
    }

    std::vector<std::uint8_t> slots_{};
    std::size_t num_slots_{0};
    std::size_t num_keys_{0};
    std::uint64_t seed_{0};
};
