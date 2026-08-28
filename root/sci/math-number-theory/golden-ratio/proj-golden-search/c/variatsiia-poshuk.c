#include <stdio.h>

/* Обчислює n-е число Фібоначчі */
static unsigned long fibonacci(int n) {
    unsigned long a = 0, b = 1;
    for (int i = 0; i < n; ++i) {
        unsigned long c = a + b;
        a = b;
        b = c;
    }
    return a;
}

double fibonacci_search(double (*func)(double), double a, double b, int n) {
    double x1 = a + (double)fibonacci(n - 2) / fibonacci(n) * (b - a);
    double x2 = a + (double)fibonacci(n - 1) / fibonacci(n) * (b - a);
    double f1 = func(x1);
    double f2 = func(x2);

    for (int k = n; k > 2; --k) {
        if (f1 < f2) {
            b = x2;
            x2 = x1;
            f2 = f1;
            x1 = a + (double)fibonacci(k - 3) / fibonacci(k - 1) * (b - a);
            f1 = func(x1);
        } else {
            a = x1;
            x1 = x2;
            f1 = f2;
            x2 = a + (double)fibonacci(k - 2) / fibonacci(k - 1) * (b - a);
            f2 = func(x2);
        }
    }
    return (a + b) / 2.0;
}
