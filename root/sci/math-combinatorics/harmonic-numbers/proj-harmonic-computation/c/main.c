#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Стала Ейлера — Маскероні з точністю до 20 знаків */
#define EULER_MASCHERONI 0.57721566490153286060

typedef struct {
    double value;
    bool is_exact;
    const char* error_message;
} HarmonicResult;

/* Обчислення гармонічного числа алгоритмом Кахана (для n <= 1000) */
static double harmonic_kahan(unsigned long long n) {
    double sum = 0.0;
    double c = 0.0;
    for (unsigned long long k = 1; k <= n; ++k) {
        double y = (1.0 / (double)k) - c;
        double t = sum + y;
        c = (t - sum) - y;
        sum = t;
    }
    return sum;
}

/* Обчислення асимптотичною формулою Ейлера — Маклорена (для n > 1000) */
static double harmonic_asymptotic(unsigned long long n) {
    double nd = (double)n;
    double n2 = nd * nd;
    double n4 = n2 * n2;
    double n6 = n4 * n2;

    return log(nd) + EULER_MASCHERONI 
           + (1.0 / (2.0 * nd)) 
           - (1.0 / (12.0 * n2)) 
           + (1.0 / (120.0 * n4)) 
           - (1.0 / (252.0 * n6));
}

/* Головна гібридна функція API на C */
HarmonicResult compute_harmonic(unsigned long long n) {
    HarmonicResult res;
    res.error_message = NULL;

    if (n == 0) {
        res.value = 0.0;
        res.is_exact = false;
        res.error_message = "Гармонічне число H[0] не визначено (n має бути >= 1)";
        return res;
    }

    if (n <= 1000) {
        res.value = harmonic_kahan(n);
        res.is_exact = true;
    } else {
        res.value = harmonic_asymptotic(n);
        res.is_exact = false;
    }

    return res;
}

int main(void) {
    unsigned long long test_values[] = {1, 5, 10, 1000, 1000000};
    size_t count = sizeof(test_values) / sizeof(test_values[0]);

    for (size_t i = 0; i < count; ++i) {
        HarmonicResult r = compute_harmonic(test_values[i]);
        if (r.error_message) {
            printf("Помилка: %s\n", r.error_message);
        } else {
            printf("H[%llu] = %.15f (%s)\n", 
                   test_values[i], r.value, 
                   r.is_exact ? "точне сумування" : "асимптотика O(1)");
        }
    }
    return 0;
}
