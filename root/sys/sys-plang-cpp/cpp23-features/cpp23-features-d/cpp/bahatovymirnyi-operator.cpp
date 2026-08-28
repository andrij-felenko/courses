template <typename T, size_t Rows, size_t Cols>
struct Matrix {
    T data[Rows * Cols];

    T& operator[](size_t r, size_t c) noexcept {
        return data[r * Cols + c];
    }

    const T& operator[](size_t r, size_t c) const noexcept {
        return data[r * Cols + c];
    }
};

Matrix<float, 4, 4> mat;
mat[1, 2] = 3.14f; // Природний математичний доступ до елемента
