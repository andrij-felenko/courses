#include <mdspan>
#include <vector>
#include <print>

void process_tensor() {
    std::vector<double> buffer(3 * 4, 0.0);

    // Створення 2D-виду розміром 3x4 поверх плоского вектора
    std::mdspan<double, std::extents<size_t, 3, 4>> matrix(buffer.data());

    // Запис через багатовимірний operator[]
    matrix[1, 2] = 42.0;

    // Стовпчик за стовпчиком (Fortran-layout) для інтеграції з LAPACK/BLAS
    std::mdspan<double, std::dextents<size_t, 2>, std::layout_left> fortran_matrix(
        buffer.data(), 3, 4
    );

    std::println("Елемент buffer[6]: {}", buffer[1 * 4 + 2]); // Друкує 42.0
}
