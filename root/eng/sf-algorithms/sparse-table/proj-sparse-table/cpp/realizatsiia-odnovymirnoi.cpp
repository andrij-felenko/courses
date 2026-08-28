#include <vector>
#include <span>
#include <bit>
#include <functional>
#include <concepts>
#include <optional>
#include <cstdint>
#include <algorithm>

/* Узагальнена шаблонна розріджена таблиця з підтримкою довільних функторів */
template <typename T, typename BinaryOp = std::ranges::min>
requires std::invocable<BinaryOp, T, T>
class SparseTable {
public:
    using value_type = T;
    using size_type = std::size_t;

    /* Конструктор із діапазону (std::span) */
    explicit SparseTable(std::span<const T> values, BinaryOp op = BinaryOp{})
        : op_(std::move(op)), n_(values.size()) 
    {
        if (n_ == 0) {
            return;
        }

        /* Обчислюємо кількість рівнів через std::bit_width (C++20) */
        levels_ = std::bit_width(n_);
        table_.resize(levels_ * n_);

        /* Рівень 0: початкові елементи */
        for (size_type i = 0; i < n_; ++i) {
            table_[0 * n_ + i] = values[i];
        }

        /* Заповнення наступних рівнів за ДП-формулою */
        for (size_type j = 1; j < levels_; ++j) {
            const size_type half = size_type{1} << (j - 1);
            const size_type len = size_type{1} << j;
            const size_type row_curr = j * n_;
            const size_type row_prev = (j - 1) * n_;

            for (size_type i = 0; i + len <= n_; ++i) {
                table_[row_curr + i] = op_(table_[row_prev + i], 
                                           table_[row_prev + i + half]);
            }
        }
    }

    /* Конструктор зі стандартного вектора */
    explicit SparseTable(const std::vector<T>& values, BinaryOp op = BinaryOp{})
        : SparseTable(std::span<const T>(values), std::move(op)) {}

    /* Константний запит O(1) для ідемпотентних операторів (min, max, gcd, AND, OR) */
    [[nodiscard]] std::optional<T> query(size_type l, size_type r) const noexcept {
        if (n_ == 0 || l > r || r >= n_) {
            return std::nullopt;
        }

        const size_type len = r - l + 1;
        /* Швидкий розрахунок k = floor(log2(len)) через bit_width */
        const size_type k = std::bit_width(len) - 1;
        const size_type shift = size_type{1} << k;

        const T& left_val = table_[k * n_ + l];
        const T& right_val = table_[k * n_ + (r - shift + 1)];

        return op_(left_val, right_val);
    }

    /* Логарифмічний запит O(log N) для неідемпотентних асоціативних операторів */
    [[nodiscard]] std::optional<T> query_disjoint(size_type l, size_type r) const noexcept {
        if (n_ == 0 || l > r || r >= n_) {
            return std::nullopt;
        }

        size_type len = r - l + 1;
        size_type curr = l;
        std::optional<T> accum = std::nullopt;

        for (size_type b = 0; b < levels_; ++b) {
            if ((len & (size_type{1} << b)) != 0) {
                const T& block_val = table_[b * n_ + curr];
                accum = accum ? op_(*accum, block_val) : block_val;
                curr += (size_type{1} << b);
            }
        }

        return accum;
    }

    [[nodiscard]] size_type size() const noexcept { return n_; }
    [[nodiscard]] bool empty() const noexcept { return n_ == 0; }

private:
    BinaryOp op_;
    size_type n_{0};
    size_type levels_{0};
    std::vector<T> table_;
};
