#include <linalg>
#include <vector>
#include <mdspan>
#include <iostream>

void matrix_multiplication_demo() {
    std::vector<double> A_data = {1, 2, 3, 4};
    std::vector<double> B_data = {5, 6, 7, 8};
    std::vector<double> C_data(4, 0.0);

    // Створюємо двовимірні неволодіючі представлення матриць 2x2
    std::mdspan A(A_data.data(), 2, 2);
    std::mdspan B(B_data.data(), 2, 2);
    std::mdspan C(C_data.data(), 2, 2);

    // Стандартне матричне множення GEMM: C = A * B
    std::linalg::matrix_product(A, B, C);

    std::cout << "C[0, 0] = " << C[0, 0] << " (очікувано 19)\n";
    std::cout << "C[0, 1] = " << C[0, 1] << " (очікувано 22)\n";
}
