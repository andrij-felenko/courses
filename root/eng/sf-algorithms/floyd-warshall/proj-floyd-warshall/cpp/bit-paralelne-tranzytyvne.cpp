#include <vector>
#include <cstdint>
#include <span>

class BitsetWarshall {
public:
    explicit BitsetWarshall(int n)
        : n_(n),
          words_per_row_((n + 63) / 64),
          rows_(static_cast<size_t>(n) * words_per_row_, 0ULL) {
        for (int i = 0; i < n_; ++i) {
            rows_[idx(i, i / 64)] |= (1ULL << (i % 64));
        }
    }

    void add_edge(int u, int v) {
        if (u >= 0 && u < n_ && v >= 0 && v < n_) {
            rows_[idx(u, v / 64)] |= (1ULL << (v % 64));
        }
    }

    void compute() {
        for (int k = 0; k < n_; ++k) {
            const size_t k_word = static_cast<size_t>(k / 64);
            const uint64_t k_mask = (1ULL << (k % 64));
            const size_t k_offset = static_cast<size_t>(k) * words_per_row_;

            for (int i = 0; i < n_; ++i) {
                const size_t i_offset = static_cast<size_t>(i) * words_per_row_;
                if (rows_[i_offset + k_word] & k_mask) {
                    for (size_t m = 0; m < words_per_row_; ++m) {
                        rows_[i_offset + m] |= rows_[k_offset + m];
                    }
                }
            }
        }
    }

    [[nodiscard]] bool is_reachable(int u, int v) const noexcept {
        if (u < 0 || u >= n_ || v < 0 || v >= n_) return false;
        const size_t offset = idx(u, v / 64);
        return (rows_[offset] & (1ULL << (v % 64))) != 0;
    }

private:
    [[nodiscard]] inline size_t idx(int row, int word_idx) const noexcept {
        return static_cast<size_t>(row) * words_per_row_ + static_cast<size_t>(word_idx);
    }

    int n_;
    size_t words_per_row_;
    std::vector<uint64_t> rows_;
};
