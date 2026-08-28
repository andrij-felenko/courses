#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

// Структура для збереження знайденої дружньої пари
typedef struct {
    uint64_t a;
    uint64_t b;
} AmicablePair;

// Функція генерації решета та відбору дружніх пар
void find_amicable_pairs_sieve(uint64_t limit) {
    // Виділяємо пам'ять під масив сум дільників.
    // Використовуємо calloc для обнулення всіх елементів.
    uint64_t *s = (uint64_t *)calloc(limit + 1, sizeof(uint64_t));
    if (!s) {
        fprintf(stderr, "Помилка: не вдалося виділити пам'ять під limit = %llu\n", 
                (unsigned long long)limit);
        return;
    }

    // Крок 1: Адитивне решето суми дільників O(N log N)
    for (uint64_t d = 1; d <= limit / 2; ++d) {
        for (uint64_t m = 2 * d; m <= limit; m += d) {
            s[m] += d;
        }
    }

    // Крок 2: Сканування та виявлення дружніх пар
    uint64_t pair_count = 0;
    printf("--- Знайдені дружні пари у діапазоні до %llu ---\n", (unsigned long long)limit);

    for (uint64_t a = 2; a <= limit; ++a) {
        uint64_t b = s[a];

        // Крихітні умови канонічності:
        // 1. a < b — забезпечує унікальність (уникаємо дублювання (b, a) та самоперевірки (a, a))
        // 2. b <= limit — запобігає виходу за межі виділеного масиву s
        // 3. s[b] == a — перевіряє взаємне повернення аліквотної суми
        if (a < b && b <= limit && s[b] == a) {
            pair_count++;
            printf("%4llu: (%llu, %llu)\n", (unsigned long long)pair_count,
                   (unsigned long long)a, (unsigned long long)b);
        }
    }

    printf("Усього знайдено пар: %llu\n", (unsigned long long)pair_count);

    // Звільняємо пам'ять
    free(s);
}

int main(void) {
    uint64_t limit = 100000;
    find_amicable_pairs_sieve(limit);
    return 0;
}
