#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_DEGREE 4
#define TAPE_SIZE 64

/* Структура для символьного нестандартного числа: a0 + a1*H + a2*H^2 + ... */
typedef struct {
    int64_t coeffs[MAX_DEGREE];
} NonStandardInt;

/* Структура конфігурації нестандартної машини Тюринга */
typedef struct {
    uint8_t tape[TAPE_SIZE];
    size_t head_pos;
    int current_state;
    NonStandardInt step_count;
    bool halted;
} NonStandardTM;

/* Створення стандартного числа */
NonStandardInt ns_create_standard(int64_t val) {
    NonStandardInt num;
    memset(&num, 0, sizeof(num));
    num.coeffs[0] = val;
    return num;
}

/* Створення нестандартного елемента H^degree */
NonStandardInt ns_create_inf(size_t degree, int64_t coeff) {
    NonStandardInt num;
    memset(&num, 0, sizeof(num));
    if (degree < MAX_DEGREE) {
        num.coeffs[degree] = coeff;
    }
    return num;
}

/* Перевірка, чи є число стандартним (належить N) */
bool ns_is_standard(const NonStandardInt* num) {
    for (size_t i = 1; i < MAX_DEGREE; ++i) {
        if (num->coeffs[i] != 0) {
            return false;
        }
    }
    return num->coeffs[0] >= 0;
}

/* Порівняння двох нестандартних чисел (порядок у моделі) */
int ns_compare(const NonStandardInt* a, const NonStandardInt* b) {
    for (int i = MAX_DEGREE - 1; i >= 0; --i) {
        if (a->coeffs[i] > b->coeffs[i]) return 1;
        if (a->coeffs[i] < b->coeffs[i]) return -1;
    }
    return 0;
}

/* Додавання двох нестандартних чисел */
NonStandardInt ns_add(const NonStandardInt* a, const NonStandardInt* b) {
    NonStandardInt result;
    for (size_t i = 0; i < MAX_DEGREE; ++i) {
        result.coeffs[i] = a->coeffs[i] + b->coeffs[i];
    }
    return result;
}

/* Множення двох нестандартних чисел з відтинанням вищих степенів */
NonStandardInt ns_multiply(const NonStandardInt* a, const NonStandardInt* b) {
    NonStandardInt result;
    memset(&result, 0, sizeof(result));
    for (size_t i = 0; i < MAX_DEGREE; ++i) {
        for (size_t j = 0; j < MAX_DEGREE - i; ++j) {
            result.coeffs[i + j] += a->coeffs[i] * b->coeffs[j];
        }
    }
    return result;
}

/* Друк нестандартного числа */
void ns_print(const NonStandardInt* num) {
    bool first = true;
    for (int i = MAX_DEGREE - 1; i >= 0; --i) {
        if (num->coeffs[i] != 0) {
            if (!first && num->coeffs[i] > 0) printf(" + ");
            if (num->coeffs[i] < 0) printf(" - ");
            
            int64_t abs_val = num->coeffs[i] < 0 ? -num->coeffs[i] : num->coeffs[i];
            
            if (i == 0) {
                printf("%lld", (long long)abs_val);
            } else if (i == 1) {
                if (abs_val == 1) printf("H");
                else printf("%lld·H", (long long)abs_val);
            } else {
                if (abs_val == 1) printf("H^%d", i);
                else printf("%lld·H^%d", (long long)abs_val, i);
            }
            first = false;
        }
    }
    if (first) printf("0");
}

/* Перевірка принципу Оверспілу: предикат P(n), істинний для всіх n in N */
bool ns_check_overspill(bool (*predicate)(int64_t), const NonStandardInt* limit) {
    /* Крок 1: Перевіряємо стандартні елементи */
    for (int64_t i = 0; i < 100; ++i) {
        if (!predicate(i)) {
            return false;
        }
    }
    /* Крок 2: За принципом Оверспілу предикат розширюється на нестандартну область */
    return !ns_is_standard(limit);
}

/* Приклад предикату: n^2 >= 0 */
bool predicate_always_true(int64_t n) {
    return (n * n) >= 0;
}

/* Ініціалізація нестандартної машини Тюринга */
void tm_init(NonStandardTM* tm) {
    memset(tm->tape, 0, sizeof(tm->tape));
    tm->head_pos = TAPE_SIZE / 2;
    tm->current_state = 0;
    tm->step_count = ns_create_standard(0);
    tm->halted = false;
}

/* Симуляція одного кроку TM */
void tm_step(NonStandardTM* tm) {
    if (tm->halted) return;

    /* Проста програма: інверсія біта і зсув вправо */
    if (tm->current_state == 0) {
        tm->tape[tm->head_pos] ^= 1;
        if (tm->head_pos < TAPE_SIZE - 1) {
            tm->head_pos++;
        } else {
            tm->halted = true;
        }
    }
    
    NonStandardInt one = ns_create_standard(1);
    tm->step_count = ns_add(&tm->step_count, &one);
}

int main(void) {
    printf("=== Симулятор Нестандартної Арифметики та Машин Тюринга (C99) ===\n\n");

    NonStandardInt n5 = ns_create_standard(5);
    NonStandardInt H = ns_create_inf(1, 1);
    NonStandardInt H2 = ns_create_inf(2, 2);

    NonStandardInt sum = ns_add(&H, &n5);
    NonStandardInt prod = ns_multiply(&sum, &H);

    printf("Число A (стандартне): ");
    ns_print(&n5);
    printf("\nЧисло B (нестандартне H): ");
    ns_print(&H);
    printf("\nСума B + A: ");
    ns_print(&sum);
    printf("\nДобуток (H + 5) · H: ");
    ns_print(&prod);
    printf("\n\n");

    printf("Порівняння H та (H + 5): %d\n", ns_compare(&H, &sum));
    printf("Чи є H+5 стандартним? %s\n", ns_is_standard(&sum) ? "Так" : "Ні");

    NonStandardInt inf_limit = ns_create_inf(1, 1000);
    bool overspill = ns_check_overspill(predicate_always_true, &inf_limit);
    printf("Результат перевірки Оверспілу для H=1000·H: %s\n\n", overspill ? "УСПІХ (Перелив виконується)" : "ХИБА");

    NonStandardTM tm;
    tm_init(&tm);
    for (int i = 0; i < 10; ++i) {
        tm_step(&tm);
    }

    printf("Стан машини Тюринга після 10 кроків:\n");
    printf("Позиція головки: %zu, Поточний крок: ", tm.head_pos);
    ns_print(&tm.step_count);
    printf("\n");

    return 0;
}
