// Файл: Matrix.hpp
template <typename T>
class Matrix {
public:
    void invert();
    void multiply(const Matrix<T>& other);
};

// Заборона генерації коду Matrix<float> у всіх файлах, які включають цей заголовок:
extern template class Matrix<float>;
extern template class Matrix<double>;
