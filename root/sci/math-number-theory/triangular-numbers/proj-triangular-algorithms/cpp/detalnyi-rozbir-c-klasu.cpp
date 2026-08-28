#include <iostream>
#include <vector>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <utility>

namespace math {

template <typename T>
class TriangularMatrix {
private:
    std::size_t dim_;
    std::vector<T> data_;

public:
    explicit TriangularMatrix(std::size_t dim)
        : dim_(dim), data_(dim * (dim + 1) / 2, T{}) {}

    std::size_t dimension() const noexcept { return dim_; }
    std::size_t capacity() const noexcept { return data_.size(); }

    // Пряма індексація
    T& operator()(std::size_t i, std::size_t j) {
        if (j > i || i >= dim_) {
            throw std::out_of_range("Індекси виходять за межі нижньотрикутної матриці");
        }
        const std::size_t flat_idx = i * (i + 1) / 2 + j;
        return data_[flat_idx];
    }

    const T& operator()(std::size_t i, std::size_t j) const {
        if (j > i || i >= dim_) {
            throw std::out_of_range("Індекси виходять за межі нижньотрикутної матриці");
        }
        const std::size_t flat_idx = i * (i + 1) / 2 + j;
        return data_[flat_idx];
    }

    // Обернена індексація (відновлення координат)
    static std::pair<std::size_t, std::size_t> inverse_map(std::size_t flat_index) noexcept {
        const std::uint64_t disc = 8 * static_cast<std::uint64_t>(flat_index) + 1;
        
        std::uint64_t s = flat_index;
        std::uint64_t y = (s + 1) / 2;
        while (y < s) {
            s = y;
            y = (s + disc / s) / 2;
        }

        const std::size_t i = static_cast<std::size_t>((s - 1) / 2);
        const std::size_t j = flat_index - i * (i + 1) / 2;
        return {i, j};
    }
};

} // namespace math
