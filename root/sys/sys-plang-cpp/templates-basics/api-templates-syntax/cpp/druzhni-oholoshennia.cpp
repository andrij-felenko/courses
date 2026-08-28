template <typename T>
class Matrix {
public:
    // Hidden Friend: створює дружній оператор для конкретного Matrix<T>
    friend std::ostream& operator<<(std::ostream& os, const Matrix<T>& m) {
        os << "[" << m.rows_ << "x" << m.cols_ << "]";
        return os;
    }

    // Дружній шаблон для міжтипових перетворень
    template <typename U>
    friend class Matrix;

private:
    std::size_t rows_{0};
    std::size_t cols_{0};
};
