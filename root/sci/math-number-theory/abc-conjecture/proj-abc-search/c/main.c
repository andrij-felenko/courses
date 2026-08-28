#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

// Структура для збереження знайденої трійки ABC
typedef struct {
    uint64_t a;
    uint64_t b;
    uint64_t c;
    uint64_t rad_abc;
    double quality;
} ABCTriple;

// Обчислення найбільшого спільного дільника (алгоритм Евкліда)
static uint64_t gcd(uint64_t a, uint64_t b) {
    while (b != 0) {
        uint64_t temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}

// Функція порівняння для qsort (сортування за спаданням якості)
static int compare_triples(const void *a, const void *b) {
    const ABCTriple *t1 = (const ABCTriple *)a;
    const ABCTriple *t2 = (const ABCTriple *)b;
    if (t2->quality > t1->quality) return 1;
    if (t2->quality < t1->quality) return -1;
    return 0;
}

// Головна функція пошуку трійок ABC
int main(void) {
    const uint64_t c_max = 10000;
    
    // Виділення пам'яті під масив радикалів
    uint64_t *rad = (uint64_t *)malloc((c_max + 1) * sizeof(uint64_t));
    if (!rad) {
        fprintf(stderr, "Помилка виділення пам'яті для масиву радикалів\n");
        return 1;
    }

    // Ініціалізація решета радикалів
    for (uint64_t i = 1; i <= c_max; ++i) {
        rad[i] = 1;
    }

    // Модифіковане решето Ератосфена для обчислення rad(n)
    for (uint64_t p = 2; p <= c_max; ++p) {
        if (rad[p] == 1) { // p — просте число
            for (uint64_t k = p; k <= c_max; k += p) {
                rad[k] *= p;
            }
        }
    }

    size_t capacity = 128;
    size_t count = 0;
    ABCTriple *triples = (ABCTriple *)malloc(capacity * sizeof(ABCTriple));
    if (!triples) {
        free(rad);
        return 1;
    }

    // Основний цикл перебору трійок a + b = c
    for (uint64_t c = 3; c <= c_max; ++c) {
        for (uint64_t a = 1; a <= c / 2; ++a) {
            uint64_t b = c - a;
            
            if (gcd(a, b) != 1) continue;

            // Захист від переповнення при множенні радикалів
            double log_c = log((double)c);
            double log_rad_a = log((double)rad[a]);
            double log_rad_b = log((double)rad[b]);
            double log_rad_c = log((double)rad[c]);
            double log_rad_abc = log_rad_a + log_rad_b + log_rad_c;

            if (log_c > log_rad_abc) {
                double q = log_c / log_rad_abc;
                uint64_t rad_abc = rad[a] * rad[b] * rad[c];
                
                if (count >= capacity) {
                    capacity *= 2;
                    ABCTriple *temp = (ABCTriple *)realloc(triples, capacity * sizeof(ABCTriple));
                    if (!temp) {
                        free(triples);
                        free(rad);
                        return 1;
                    }
                    triples = temp;
                }
                
                triples[count].a = a;
                triples[count].b = b;
                triples[count].c = c;
                triples[count].rad_abc = rad_abc;
                triples[count].quality = q;
                count++;
            }
        }
    }

    // Сортування знайдених трійок за спаданням якості
    qsort(triples, count, sizeof(ABCTriple), compare_triples);

    // Вивід топрезультатів
    printf("Знайдено %zu трійок ABC для c <= %llu:\n", count, (unsigned long long)c_max);
    printf("%-8s %-8s %-8s %-12s %-8s\n", "a", "b", "c", "rad(abc)", "Якість (q)");
    printf("--------------------------------------------------\n");

    size_t print_limit = count < 10 ? count : 10;
    for (size_t i = 0; i < print_limit; ++i) {
        printf("%-8llu %-8llu %-8llu %-12llu %-8.4f\n",
               (unsigned long long)triples[i].a,
               (unsigned long long)triples[i].b,
               (unsigned long long)triples[i].c,
               (unsigned long long)triples[i].rad_abc,
               triples[i].quality);
    }

    free(triples);
    free(rad);
    return 0;
}
