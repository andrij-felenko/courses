#include <iostream>
#include <vector>
#include <cstdint>
#include <bitset>
#include <span>
#include <optional>
#include <bit>
#include <numeric>
#include <stdexcept>

class PaleyGraph {
public:
    explicit PaleyGraph(uint32_t p) : p_(p), words_per_row_((p + 63) / 64) {
        if (p < 5 || (p % 4) != 1) {
            throw std::invalid_argument("Порядок графа Пейлі повинен бути p = 1 (mod 4) та p >= 5");
        }

        is_square_.resize(p_, false);
        adj_.resize(p_ * words_per_row_, 0);

        // 1. Попередня генерація квадратичних залишків: x^2 mod p
        for (uint32_t x = 1; x <= p_ / 2; ++x) {
            uint32_t sq = static_cast<uint32_t>((static_cast<uint64_t>(x) * x) % p_);
            is_square_[sq] = true;
        }

        // 2. Побудова бітової матриці суміжності
        for (uint32_t u = 0; u < p_; ++u) {
            for (uint32_t v = 0; v < p_; ++v) {
                if (u == v) continue;
                uint32_t diff = (u >= v) ? (u - v) : (u + p_ - v);
                if (is_square_[diff]) {
                    uint32_t idx = u * words_per_row_ + (v / 64);
                    adj_[idx] |= (1ULL << (v % 64));
                }
            }
        }
    }

    [[nodiscard]] uint32_t order() const noexcept { return p_; }
    [[nodiscard]] uint32_t words_per_row() const noexcept { return words_per_row_; }

    [[nodiscard]] bool are_adjacent(uint32_t u, uint32_t v) const noexcept {
        if (u >= p_ || v >= p_ || u == v) return false;
        uint32_t idx = u * words_per_row_ + (v / 64);
        return (adj_[idx] & (1ULL << (v % 64))) != 0;
    }

    [[nodiscard]] uint32_t common_neighbours(uint32_t u, uint32_t v) const noexcept {
        if (u >= p_ || v >= p_) return 0;
        uint32_t count = 0;
        uint32_t offset_u = u * words_per_row_;
        uint32_t offset_v = v * words_per_row_;

        for (uint32_t w = 0; w < words_per_row_; ++w) {
            uint64_t mask = adj_[offset_u + w] & adj_[offset_v + w];
            count += static_cast<uint32_t>(std::popcount(mask));
        }
        return count;
    }

    struct SrgParams {
        uint32_t v, k, lambda, mu;
    };

    [[nodiscard]] std::optional<SrgParams> verify_srg() const noexcept {
        uint32_t expected_k = (p_ - 1) / 2;
        uint32_t expected_lambda = (p_ - 5) / 4;
        uint32_t expected_mu = (p_ - 1) / 4;

        // Перевірка степенів вершин
        for (uint32_t u = 0; u < p_; ++u) {
            uint32_t deg = 0;
            uint32_t offset = u * words_per_row_;
            for (uint32_t w = 0; w < words_per_row_; ++w) {
                deg += static_cast<uint32_t>(std::popcount(adj_[offset + w]));
            }
            if (deg != expected_k) return std::nullopt;
        }

        // Перевірка кількості спільних сусідів
        for (uint32_t u = 0; u < p_; ++u) {
            for (uint32_t v = u + 1; v < p_; ++v) {
                uint32_t common = common_neighbours(u, v);
                bool adj = are_adjacent(u, v);
                if (adj && common != expected_lambda) return std::nullopt;
                if (!adj && common != expected_mu) return std::nullopt;
            }
        }

        return SrgParams{p_, expected_k, expected_lambda, expected_mu};
    }

    [[nodiscard]] std::span<const uint64_t> row_bitset(uint32_t u) const noexcept {
        return std::span<const uint64_t>(adj_.data() + u * words_per_row_, words_per_row_);
    }

private:
    uint32_t p_;
    uint32_t words_per_row_;
    std::vector<bool> is_square_;
    std::vector<uint64_t> adj_;
};
