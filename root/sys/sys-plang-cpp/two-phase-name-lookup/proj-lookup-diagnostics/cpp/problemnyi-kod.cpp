#include <iostream>

namespace math {
    template <typename T>
    class Matrix {
        T value;
    public:
        Matrix(T v) : value(v) {}

        // Прихована функція-друг: оголошена ВСЕРЕДИНІ класу!
        // Вона НЕ бачиться через звичайний пошук у просторі math::
        friend Matrix operator+(const Matrix& a, const Matrix& b) {
            return Matrix(a.value + b.value);
        }

        friend void print_matrix(const Matrix& m) {
            std::cout << "Matrix value: " << m.value << "\n";
        }
    };
}

template <typename T>
void algorithm(T a, T b) {
    // Незалежний або залежний виклик?
    // math::Matrix<int> є залежним типом від T.
    auto res = a + b;       // Працює через ADL на Фазі 2
    print_matrix(res);     // Працює через ADL на Фазі 2
}

void global_helper() {
    // ПОМИЛКА: Звичайний некваліфікований пошук НЕ знаходить print_matrix!
    // print_matrix(math::Matrix<int>(5)); 
}
