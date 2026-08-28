/* src/calc.c — обчислювальний модуль мовою C */
#include <stdio.h>

long long compute_factorial(int n) {
    if (n <= 1) return 1;
    long long result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

int main(void) {
    int val = 10;
    printf("Факторіал %d = %lld\n", val, compute_factorial(val));
    return 0;
}
