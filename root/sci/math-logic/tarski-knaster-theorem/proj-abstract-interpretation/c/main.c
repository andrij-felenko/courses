#include <stdio.h>
#include <stdbool.h>
#include <limits.h>

/* Позначення нескінченностей через безпечні константи */
#define INF_POS  (LONG_MAX / 2)
#define INF_NEG  (LONG_MIN / 2)

/* Структура інтервалу в ґратці L_int */
typedef struct {
    long min;
    long max;
    bool is_bottom;
} Interval;

/* Створення найменшого елемента ґратки (ботом) */
static inline Interval interval_bottom(void) {
    Interval iv = {0, 0, true};
    return iv;
}

/* Створення інтервалу з перевіркою коректності меж */
static inline Interval interval_create(long min, long max) {
    if (min > max) return interval_bottom();
    Interval iv = {min, max, false};
    return iv;
}

/* Порівняння двох інтервалів на точну рівність */
static inline bool interval_equals(Interval a, Interval b) {
    if (a.is_bottom && b.is_bottom) return true;
    if (a.is_bottom || b.is_bottom) return false;
    return a.min == b.min && a.max == b.max;
}

/* Операція точної верхньої грані (Join, ⊔) */
static inline Interval interval_join(Interval a, Interval b) {
    if (a.is_bottom) return b;
    if (b.is_bottom) return a;
    long min = (a.min < b.min) ? a.min : b.min;
    long max = (a.max > b.max) ? a.max : b.max;
    return interval_create(min, max);
}

/* Операція точної нижньої грані (Meet, ⊓) */
static inline Interval interval_meet(Interval a, Interval b) {
    if (a.is_bottom || b.is_bottom) return interval_bottom();
    long min = (a.min > b.min) ? a.min : b.min;
    long max = (a.max < b.max) ? a.max : b.max;
    return interval_create(min, max);
}

/* Абстрактний трансформатор додавання константи */
static inline Interval interval_add_const(Interval a, long val) {
    if (a.is_bottom) return interval_bottom();
    long min = (a.min <= INF_NEG) ? INF_NEG : a.min + val;
    long max = (a.max >= INF_POS) ? INF_POS : a.max + val;
    return interval_create(min, max);
}

/* Оператор розширення (Widening, ∇) для швидкої збіжності */
static inline Interval interval_widen(Interval prev, Interval next) {
    if (prev.is_bottom) return next;
    if (next.is_bottom) return prev;
    long min = (next.min < prev.min) ? INF_NEG : prev.min;
    long max = (next.max > prev.max) ? INF_POS : prev.max;
    return interval_create(min, max);
}

/* Оператор звуження (Narrowing, Δ) для відновлення точності */
static inline Interval interval_narrow(Interval prev, Interval next) {
    if (prev.is_bottom || next.is_bottom) return interval_bottom();
    long min = (prev.min <= INF_NEG) ? next.min : prev.min;
    long max = (prev.max >= INF_POS) ? next.max : prev.max;
    return interval_create(min, max);
}

/* Друк інтервалу в консоль */
static void print_interval(const char *label, Interval iv) {
    printf("%-22s: ", label);
    if (iv.is_bottom) {
        printf("⊥ (недосяжний стан)\n");
    } else {
        printf("[");
        if (iv.min <= INF_NEG) printf("-∞"); else printf("%ld", iv.min);
        printf(", ");
        if (iv.max >= INF_POS) printf("+∞"); else printf("%ld", iv.max);
        printf("]\n");
    }
}

int main(void) {
    /* Моделюємо аналіз програми:
       int x = 0;
       while (x < 100) {
           x = x + 1;
       }
    */
    Interval init_state = interval_create(0, 0);
    Interval loop_head = interval_bottom();
    Interval guard = interval_create(INF_NEG, 99);

    /* Етап 1: Пошук постфіксної точки з розширенням (Widening) */
    printf("=== Етап 1: Ітерація розширення (Widening) ===\n");
    for (int iter = 1; iter <= 10; ++iter) {
        Interval in_loop = interval_meet(loop_head, guard);
        Interval step = interval_add_const(in_loop, 1);
        Interval combined = interval_join(init_state, step);
        Interval next_head = interval_widen(loop_head, combined);

        printf("Ітерація %d: ", iter);
        print_interval("loop_head", next_head);

        if (interval_equals(loop_head, next_head)) {
            printf("Постфіксну точку стабілізовано на кроці %d.\n\n", iter);
            break;
        }
        loop_head = next_head;
    }

    /* Етап 2: Уточнення значень оператором звуження (Narrowing) */
    printf("=== Етап 2: Ітерація звуження (Narrowing) ===\n");
    for (int iter = 1; iter <= 5; ++iter) {
        Interval in_loop = interval_meet(loop_head, guard);
        Interval step = interval_add_const(in_loop, 1);
        Interval combined = interval_join(init_state, step);
        Interval next_head = interval_narrow(loop_head, combined);

        printf("Ітерація %d: ", iter);
        print_interval("loop_head", next_head);

        if (interval_equals(loop_head, next_head)) {
            printf("Найменшу нерухому точку знайдено на кроці %d.\n\n", iter);
            break;
        }
        loop_head = next_head;
    }

    /* Фінальні інваріанти за теоремою Тарського — Кнастера */
    Interval body_inv = interval_meet(loop_head, guard);
    Interval exit_guard = interval_create(100, INF_POS);
    Interval exit_inv = interval_meet(loop_head, exit_guard);

    printf("=== Результати аналізу програми ===\n");
    print_interval("Інваріант на вході в цикл", loop_head);
    print_interval("Інваріант у тілі циклу", body_inv);
    print_interval("Інваріант на виході з циклу", exit_inv);

    return 0;
}
