#include <iostream>
#include <vector>
#include <cstddef>
#include <stdexcept>

namespace math {

template <typename T>
class TetrahedralTensor3D {
private:
    std::size_t dim_;
    std::vector<T> data_;

public:
    explicit TetrahedralTensor3D(std::size_t dim)
        : dim_(dim), data_(dim * (dim + 1) * (dim + 2) / 6, T{}) {}

    std::size_t dimension() const noexcept { return dim_; }
    std::size_t capacity() const noexcept { return data_.size(); }

    T& operator()(std::size_t i, std::size_t j, std::size_t k) {
        if (k > j || j > i || i >= dim_) {
            throw std::out_of_range("Некоректні індекси 3D тетраедричного тензора");
        }
        const std::size_t flat_idx = i * (i + 1) * (i + 2) / 6 + j * (j + 1) / 2 + k;
        return data_[flat_idx];
    }
};

} // namespace math
