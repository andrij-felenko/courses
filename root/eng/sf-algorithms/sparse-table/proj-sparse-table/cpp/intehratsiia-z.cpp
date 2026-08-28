#include <memory_resource>
#include <vector>
#include <array>
#include <span>
#include <bit>
#include <cstdint>
#include <algorithm>

/* Таблиця розрідження з підтримкою PMR-алокаторів */
template <typename T>
class PmrSparseTable {
public:
    using allocator_type = std::pmr::polymorphic_allocator<T>;

    PmrSparseTable(std::span<const T> values, 
                   allocator_type alloc = {})
        : n_(values.size()), table_(alloc) 
    {
        if (n_ == 0) return;
        levels_ = std::bit_width(n_);
        table_.resize(levels_ * n_);

        for (std::size_t i = 0; i < n_; ++i) table_[i] = values[i];

        for (std::size_t j = 1; j < levels_; ++j) {
            const std::size_t half = std::size_t{1} << (j - 1);
            const std::size_t row_curr = j * n_;
            const std::size_t row_prev = (j - 1) * n_;

            for (std::size_t i = 0; i + (std::size_t{1} << j) <= n_; ++i) {
                table_[row_curr + i] = std::min(table_[row_prev + i], 
                                                table_[row_prev + i + half]);
            }
        }
    }

    [[nodiscard]] T query(std::size_t l, std::size_t r) const noexcept {
        const std::size_t len = r - l + 1;
        const std::size_t k = std::bit_width(len) - 1;
        const std::size_t shift = std::size_t{1} << k;
        return std::min(table_[k * n_ + l], table_[k * n_ + (r - shift + 1)]);
    }

private:
    std::size_t n_{0};
    std::size_t levels_{0};
    std::pmr::vector<T> table_;
};
