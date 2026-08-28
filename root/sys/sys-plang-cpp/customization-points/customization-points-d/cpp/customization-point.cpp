#include <concepts>
#include <utility>
#include <vector>
#include <iostream>

namespace custom {
    struct Matrix {
        int rows, cols;
        std::vector<double> data;

        // Користувацька точка налаштування swap
        friend void swap(Matrix& a, Matrix& b) noexcept {
            std::swap(a.rows, b.rows);
            std::swap(a.cols, b.cols);
            a.data.swap(b.data);
        }
    };
}

int main() {
    custom::Matrix m1{2, 2, {1.0, 2.0, 3.0, 4.0}};
    custom::Matrix m2{2, 2, {5.0, 6.0, 7.0, 8.0}};

    // Прямий, безпечний виклик CPO без using std::swap
    std::ranges::swap(m1, m2);

    std::cout << "m1 first element: " << m1.data[0] << "\n"; // Повертає 5.0
}
