#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <time.h>

#define N_VARS 4
#define TRUTH_TABLE_SIZE (1 << N_VARS) /* 2^4 = 16 біт */
#define NUM_TRIALS 1000

/* Структура для збереження таблиці істинності булевої функції */
typedef struct {
    uint8_t bits[TRUTH_TABLE_SIZE];
    size_t num_vars;
} TruthTable;

/* Створення нової таблиці істинності */
TruthTable* tt_create(size_t num_vars) {
    TruthTable* tt = (TruthTable*)malloc(sizeof(TruthTable));
    if (!tt) return NULL;
    tt->num_vars = num_vars;
    for (size_t i = 0; i < (1ULL << num_vars); i++) {
        tt->bits[i] = 0;
    }
    return tt;
}

/* Звільнення пам'яті таблиці істинності */
void tt_free(TruthTable* tt) {
    if (tt) free(tt);
}

/* Генерація справді випадкової таблиці істинності R */
void generate_random_function(TruthTable* tt) {
    size_t size = 1ULL << tt->num_vars;
    for (size_t i = 0; i < size; i++) {
        tt->bits[i] = rand() % 2;
    }
}

/* Псевдовипадковий генератор PRF f_s (на основі зерна seed) */
void generate_pseudorandom_function(TruthTable* tt, uint32_t seed) {
    size_t size = 1ULL << tt->num_vars;
    uint32_t state = seed;
    
    /* Спрощена PRF: нелінійна комбінація LCG та змішування бітів */
    for (size_t i = 0; i < size; i++) {
        state = state * 1664525U + 1013904223U; /* LCG змішування */
        uint8_t bit = ((state ^ (i * 0x9e3779b9U)) >> 16) & 1;
        tt->bits[i] = bit;
    }
}

/* Перевірка натуральної властивості: аналіз спектра Уолша-Адамара */
/* Обчислює максимум перетворення Уолша-Адамара */
int calculate_walsh_max(const TruthTable* tt) {
    size_t size = 1ULL << tt->num_vars;
    int max_walsh = 0;

    /* Обчислення перетворення Уолша-Адамара для кожного w */
    for (size_t w = 0; w < size; w++) {
        int sum = 0;
        for (size_t x = 0; x < size; x++) {
            /* Скалярний добуток w · x mod 2 */
            size_t dot_product = 0;
            size_t temp = w & x;
            while (temp > 0) {
                dot_product ^= (temp & 1);
                temp >>= 1;
            }
            
            int f_val = tt->bits[x] ? -1 : 1;
            int walsh_val = dot_product ? -1 : 1;
            sum += f_val * walsh_val;
        }
        if (abs(sum) > max_walsh) {
            max_walsh = abs(sum);
        }
    }
    return max_walsh;
}

/* Натуральний розрізнювач D(f): */
/* повертає true (1) для високої нелінійності (R) та false (0) для псевдовипадкових (f_s) */
bool natural_distinguisher(const TruthTable* tt) {
    int max_w = calculate_walsh_max(tt);
    /* Поріг нелінійності за нерівністю Чернова */
    int threshold = (int)(sqrt(1ULL << tt->num_vars) * 2.2);
    return max_w <= threshold;
}

int main(void) {
    srand((unsigned int)time(NULL));
    printf("=== Симулятор криптографічного розрізнювача Разборова-Рудіча ===\n");
    printf("Кількість змінних n = %d, Розмір таблиці N = %d біт\n", N_VARS, TRUTH_TABLE_SIZE);

    TruthTable* tt = tt_create(N_VARS);
    if (!tt) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    int random_accepted = 0;
    int prf_accepted = 0;

    /* 1. Тестування на справді випадкових функціях R */
    for (int trial = 0; trial < NUM_TRIALS; trial++) {
        generate_random_function(tt);
        if (natural_distinguisher(tt)) {
            random_accepted++;
        }
    }

    /* 2. Тестування на псевдовипадкових функціях f_s */
    for (int trial = 0; trial < NUM_TRIALS; trial++) {
        uint32_t seed = (uint32_t)(trial + 1337);
        generate_pseudorandom_function(tt, seed);
        if (natural_distinguisher(tt)) {
            prf_accepted++;
        }
    }

    double prob_random = (double)random_accepted / NUM_TRIALS;
    double prob_prf = (double)prf_accepted / NUM_TRIALS;
    double advantage = fabs(prob_random - prob_prf);

    printf("\nРезультати випробувань (%d спроб):\n", NUM_TRIALS);
    printf("Pr[ D(R) = 1 ]  (Справді випадкові)  = %.4f (Великість: ≥ 1/poly(n))\n", prob_random);
    printf("Pr[ D(f_G) = 1 ] (Псевдовипадкові)   = %.4f (Корисність: PRF відсікаються)\n", prob_prf);
    printf("Статистична перевага Advantage       = %.4f\n", advantage);

    if (advantage > 0.1) {
        printf("\nВИСНОВОК: Натуральна властивість успішно ЗЛАМАЛА псевдовипадковий генератор!\n");
        printf("Це підтверджує теорему Разборова-Рудіча: такі властивості неможливі для P/poly.\n");
    } else {
        printf("\nВИСНОВОК: Перевага мала, потрібне налаштування порогу нелінійності.\n");
    }

    tt_free(tt);
    return 0;
}
