#include <iostream>
#include <cmath>
#include <array>

int main() {
    std::array<double, 3> a_hat = { 5.45, 12.35, 8.85 };

    std::array<int64_t, 3> a_round = {
        static_cast<int64_t>(std::round(a_hat[0])),
        static_cast<int64_t>(std::round(a_hat[1])),
        static_cast<int64_t>(std::round(a_hat[2]))
    };

    std::array<int64_t, 3> a_lambda = { 5, 12, 9 };

    std::cout << "Плаваючий вектор (float):   [ " << a_hat[0] << ", " << a_hat[1] << ", " << a_hat[2] << " ]\n";
    std::cout << "Наївне округлення [a]:      [ " << a_round[0] << ", " << a_round[1] << ", " << a_round[2] << " ]\n";
    std::cout << "Розв'язок LAMBDA (fix):     [ " << a_lambda[0] << ", " << a_lambda[1] << ", " << a_lambda[2] << " ]\n";

    return 0;
}
