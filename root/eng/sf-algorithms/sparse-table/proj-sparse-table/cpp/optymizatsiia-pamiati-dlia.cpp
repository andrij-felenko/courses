#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <algorithm>

/* Повністю статична таблиця розрідження часу компіляції */
template <typename T, std::size_t MaxN>
class StaticSparseTable {
public:
    static constexpr std::size_t MaxLevels = std::bit_width(MaxN);

    constexpr void build(const T* data, std::size_t n) noexcept {
        size_ = std::min(n, MaxN);
        levels_ = std::bit_width(size_);

        for (std::size_t i = 0; i < size_; ++i) {
            table_[0][i] = data[i];
        }

        for (std::size_t j = 1; j < levels_; ++j) {
            const std::size_t half = std::size_t{1} << (j - 1);
            for (std::size_t i = 0; i + (std::size_t{1} << j) <= size_; ++i) {
                table_[j][i] = std::min(table_[j - 1][i], table_[j - 1][i + half]);
            }
        }
    }

    [[nodiscard]] constexpr T query(std::size_t l, std::size_t r) const noexcept {
        const std::size_t len = r - l + 1;
        const std::size_t k = std::bit_width(len) - 1;
        const std::size_t shift = std::size_t{1} << k;

        return std::min(table_[k][l], table_[k][r - shift + 1]);
    }

private:
    std::size_t size_{0};
    std::size_t levels_{0};
    std::array<std::array<T, MaxN>, MaxLevels> table_{};
};
