template<typename T>
class Matrix2D {
public:
    Matrix2D(size_t rows, size_t cols)
        : rows_(rows), cols_(cols), data_(rows * cols) {}

    T& at(size_t r, size_t c) { return data_[r * cols_ + c]; }

    // Ітератор для обходу c-го стовпчика матриці
    auto column_begin(size_t col_index) {
        return StrideIterator(data_.begin() + col_index, cols_);
    }

    auto column_end(size_t col_index) {
        return StrideIterator(data_.begin() + col_index + rows_ * cols_, cols_);
    }

private:
    size_t rows_;
    size_t cols_;
    std::vector<T> data_;
};
