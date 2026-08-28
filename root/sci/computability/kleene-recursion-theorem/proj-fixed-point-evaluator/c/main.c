#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

/* Тип покажчика на функцію кроку, що обчислює значення */
typedef uint64_t (*step_fn_t)(void *ctx, uint64_t n);

/* Функціонал вищого порядку: приймає функцію кроку, контекст та аргумент n */
typedef uint64_t (*generator_fn_t)(step_fn_t recurse, void *ctx, uint64_t n);

/* Структура контексту оператора нерухомої точки */
typedef struct {
    generator_fn_t generator;
    uint64_t *memo_table;
    size_t memo_size;
} fix_context_t;

/* Внутрішній диспетчер розгортання нерухомої точки (Z-комбінатор) */
static uint64_t fix_dispatch(void *ctx, uint64_t n) {
    fix_context_t *fix_ctx = (fix_context_t *)ctx;
    /* Перевірка таблиці мемоізації для оптимізації рекурсивного дерева */
    if (fix_ctx->memo_table != NULL && n < fix_ctx->memo_size) {
        if (fix_ctx->memo_table[n] != 0 || n == 0) {
            if (n == 0 && fix_ctx->memo_table[0] == 0) {
                /* Значення 0 для бази Фібоначчі */
            } else {
                return fix_ctx->memo_table[n];
            }
        }
    }

    /* Викликаємо генератор, передаючи диспетчер як функцію наступного кроку */
    uint64_t result = fix_ctx->generator(fix_dispatch, fix_ctx, n);

    if (fix_ctx->memo_table != NULL && n < fix_ctx->memo_size) {
        fix_ctx->memo_table[n] = result;
    }
    return result;
}

/* Генератор факторіалу: анонімна функція без явного імені рекурсії */
static uint64_t fact_generator(step_fn_t self, void *ctx, uint64_t n) {
    if (n == 0) return 1;
    return n * self(ctx, n - 1);
}

/* Генератор чисел Фібоначчі */
static uint64_t fib_generator(step_fn_t self, void *ctx, uint64_t n) {
    if (n == 0) return 0;
    if (n == 1) return 1;
    return self(ctx, n - 1) + self(ctx, n - 2);
}

int main(void) {
    fix_context_t fact_fix = { .generator = fact_generator, .memo_table = NULL, .memo_size = 0 };

    /* Таблиця мемоізації для обчислення Фібоначчі за лінійний час O(n) */
    uint64_t fib_memo[100] = {0};
    fix_context_t fib_fix  = { .generator = fib_generator, .memo_table = fib_memo, .memo_size = 100 };

    uint64_t n = 10;
    uint64_t res_fact = fix_dispatch(&fact_fix, n);
    uint64_t res_fib  = fix_dispatch(&fib_fix, n);

    printf("Факторіал %llu через нерухому точку = %llu\n", 
           (unsigned long long)n, (unsigned long long)res_fact);
    printf("Фібоначчі %llu через мемоізовану нерухому точку = %llu\n", 
           (unsigned long long)n, (unsigned long long)res_fib);

    return 0;
}
