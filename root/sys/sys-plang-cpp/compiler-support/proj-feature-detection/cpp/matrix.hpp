// compat/matrix.hpp
#pragma once

#include <vector>
#include <cstddef>
#include <stdexcept>

#include "version_check.hpp"

namespace compat {

template <typename T>
class Matrix2D {
public:
    Matrix2D(size_t rows, size_t cols)
        : rows_(rows), cols_(cols), data_(rows * cols) {}

    // Традиційний синтаксис виклику (доступний у всіх стандартах)
    T& operator()(size_t r, size_t c) {
        return data_[index(r, c)];
    }

    const T& operator()(size_t r, size_t c) const {
        return data_[index(r, c)];
    }

#if defined(__cpp_multidimensional_subscript) && (__cpp_multidimensional_subscript >= 202110L)
    // Сучасний синтаксис C++23: matrix[row, col]
    T& operator[](size_t r, size_t c) {
        return data_[index(r, c)];
    }

    const T& operator[](size_t r, size_t c) const {
        return data_[index(r, c)];
    }
#endif

    size_t rows() const noexcept { return rows_; }
    size_t cols() const noexcept { return cols_; }

private:
    size_t index(size_t r, size_t c) const {
        if (r >= rows_ || c >= cols_) {
            throw std::out_of_range("Matrix index out of bounds");
        }
        return r * cols_ + c;
    }

    size_t rows_;
    size_t cols_;
    std::vector<T> data_;
};

} // namespace compat
