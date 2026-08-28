// Прикидка вихідних частот дільника 4040
#include <cstdint>
#include <iostream>

int main() {
    double f_clk = 32768.0;          // вхідний такт, Гц (годинниковий кварц)
    for (int n = 1; n <= 12; ++n) {  // 4040 має 12 розрядів: Q1..Q12
        double f_out = f_clk / (1u << n);   // Qn = такт / 2^n
        std::printf("Q%-2d = %.4f Hz\n", n, f_out);
    }
    return 0;                         // Q12 = 8 Hz; для рівно 1 Гц треба 15 розрядів (2¹⁵)
}
