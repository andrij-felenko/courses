#include <iostream>
#include <vector>
#include <span>
#include <gmp.h>
#include <gmpxx.h>

// Високоточне обчислення B_n за допомогою бібліотеки GMP (mpq_class) з підтримкою RAII
std::vector<mpq_class> compute_bernoulli_gmp(int n) {
    std::vector<mpq_class> A(n + 1);
    std::vector<mpq_class> B(n + 1);

    // Крок 1: Ініціалізація робочого масиву A[j] = 1 / (j + 1)
    for (int j = 0; j <= n; ++j) {
        A[j] = mpq_class(1, j + 1);
        A[j].canonicalize(); // Обов'язкове скорочення дробу
    }

    B[0] = A[0];

    // Крок 2: Двовимірне оновлення масиву A
    for (int i = 1; i <= n; ++i) {
        for (int j = 0; j <= n - i; ++j) {
            A[j] = (A[j] - A[j + 1]) * (j + 1);
            A[j].canonicalize();
        }
        if (i == 1) {
            B[1] = -A[0];
        } else {
            B[i] = A[0];
        }
    }

    return B;
}

// Функція безпечного виведення великого числа Бернуллі B_n через std::span
void print_bernoulli_gmp(std::span<const mpq_class> B, int index) {
    if (index < 0 || static_cast<size_t>(index) >= B.size()) {
        std::cerr << "Індекс поза межами масиву\n";
        return;
    }
    std::cout << "B_" << index << " = " << B[index].get_str() << "\n";
}
