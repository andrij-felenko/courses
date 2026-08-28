// Файл: math_matrix.ixx (або .cppm)
export module math.matrix;

import <vector>;
import <stdexcept>;

export namespace math {
    template<typename T>
    class Matrix {
    public:
        Matrix(std::size_t r, std::size_t c) : rows_(r), cols_(c), data_(r * c) {}

        T& at(std::size_t r, std::size_t c) {
            if (r >= rows_ || c >= cols_) throw std::out_of_range("Matrix bounds");
            return data_[r * cols_ + c];
        }

    private:
        std::size_t rows_, cols_;
        std::vector<T> data_;
    };

    export template<typename T>
    Matrix<T> identity(std::size_t n);
}
