#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int start_index; // Початковий індекс підмасиву (включно)
    int end_index;   // Кінцевий індекс підмасиву (включно)
    long long sum;   // Обчислена сума підмасиву
    int found;       // Прапор успішного знаходження (1 — знайдено, 0 — ні)
} SubarrayResult;

SubarrayResult find_zero_sum_mod_n(const int* arr, size_t n) {
    SubarrayResult res = { -1, -1, 0, 0 };
    if (n == 0 || arr == NULL) return res;

    // Масив для фіксації першої позиції кожної остачі (ініціалізуємо значенням -1)
    int* pos = (int*)malloc(n * sizeof(int));
    if (!pos) return res;

    for (size_t k = 0; k < n; ++k) {
        pos[k] = -1;
    }

    // Остача 0 зафіксована на префіксі довжиною 0 (перед початком масиву)
    pos[0] = 0;

    long long current_sum = 0;
    for (size_t j = 1; j <= n; ++j) {
        current_sum += arr[j - 1];

        // Коректне обчислення математичного модуля для від'ємних чисел
        long long mod_raw = current_sum % (long long)n;
        int rem = (int)((mod_raw + (long long)n) % (long long)n);

        if (pos[rem] != -1) {
            // Знайдено колізію остач за принципом Діріхле!
            res.start_index = pos[rem];       // Індекс початку (0-based)
            res.end_index = (int)j - 1;       // Індекс кінця (0-based)
            res.sum = current_sum;
            res.found = 1;
            free(pos);
            return res;
        }

        pos[rem] = (int)j;
    }

    free(pos);
    return res;
}

int main(void) {
    int data[] = { 4, -7, 2, 9, -5 };
    size_t n = sizeof(data) / sizeof(data[0]);

    SubarrayResult res = find_zero_sum_mod_n(data, n);
    if (res.found) {
        printf("Знайдено підмасив [індекси %d..%d]: ", res.start_index, res.end_index);
        long long sub_sum = 0;
        for (int k = res.start_index; k <= res.end_index; ++k) {
            printf("%d ", data[k]);
            sub_sum += data[k];
        }
        printf("\nСума підмасиву = %lld (кратно %zu)\n", sub_sum, n);
    } else {
        printf("Помилка: підмасив не знайдено (математично неможливо для N > 0).\n");
    }

    return 0;
}
