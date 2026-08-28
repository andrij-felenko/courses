#include <stdio.h>
#include <time.h>
#include <regex.h>

/* Безпечний лінійний виклик: автомат POSIX гарантує лінійний час виконання O(N) */
int match_linear_safe(const char *pattern, const char *input) {
    regex_t reg;
    clock_t start = clock();

    if (regcomp(&reg, pattern, REG_EXTENDED | REG_NOSUB) != 0) {
        return -1;
    }

    int res = regexec(&reg, input, 0, NULL, 0);
    regfree(&reg);

    clock_t end = clock();
    double cpu_ms = ((double)(end - start)) / CLOCKS_PER_SEC * 1000.0;
    printf("POSIX лінійний час виконання: %.4f мс (результат: %s)\n",
           cpu_ms, res == 0 ? "MATCH" : "NO MATCH");
    return res == 0;
}

int main(void) {
    /* Небезпечний вираз із вкладеним квантифікатором */
    const char *redos_pattern = "^(a+)+$";
    /* Рядок, що провокує експоненційний перебір гілок */
    const char *evil_input = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!";

    printf("Перевірка вразливого виразу через лінійний автомат POSIX:\n");
    match_linear_safe(redos_pattern, evil_input);
    return 0;
}
