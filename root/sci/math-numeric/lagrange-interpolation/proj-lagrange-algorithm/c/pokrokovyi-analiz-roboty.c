#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/**
 * Обчислення значення інтерполяційного многочлена Лагранжа у точці x.
 * 
 * @param x_nodes Масив x-координат вузлів (розмір n)
 * @param y_nodes Масив y-координат вузлів (розмір n)
 * @param n Кількість вузлів інтерполяції
 * @param target_x Точка, у якій необхідно обчислити значення
 * @return Обчислене значення P(target_x)
 */
double lagrange_naive_eval(const double* x_nodes, const double* y_nodes, size_t n, double target_x) {
    double result = 0.0;

    for (size_t k = 0; k < n; ++k) {
        // Перевіряємо точний збіг з вузлом для уникнення ділення на нуль
        if (fabs(target_x - x_nodes[k]) < 1e-12) {
            return y_nodes[k];
        }

        double term = y_nodes[k];
        for (size_t j = 0; j < n; ++j) {
            if (j != k) {
                double denom = x_nodes[k] - x_nodes[j];
                if (fabs(denom) < 1e-15) {
                    // Випадкові однакові x-вузли недопустимі
                    return NAN;
                }
                term *= (target_x - x_nodes[j]) / denom;
            }
        }
        result += term;
    }

    return result;
}

int main(void) {
    // Приклад: f(x) = x^2 у точках x = 1, 2, 4
    double x[3] = {1.0, 2.0, 4.0};
    double y[3] = {1.0, 4.0, 16.0};

    double test_x = 3.0;
    double eval_y = lagrange_naive_eval(x, y, 3, test_x);

    printf("P(%.1f) = %.4f (Очікується: 9.0000)\n", test_x, eval_y);
    return 0;
}
