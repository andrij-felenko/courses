#include <stdio.h>
#include <stdbool.h>
#include <limits.h>

#define INF INT_MAX
#define NEG_INF INT_MIN

typedef struct {
    int min_val;
    int max_val;
    bool is_bottom; // Порожній / недосяжний стан
} Interval;

// Створення інтервалу [min, max]
Interval make_interval(int min_val, int max_val) {
    if (min_val > max_val) {
        Interval bot = {0, 0, true};
        return bot;
    }
    Interval iv = {min_val, max_val, false};
    return iv;
}

Interval make_bottom(void) {
    Interval bot = {0, 0, true};
    return bot;
}

// Операція об'єднання двох інтервалів (Join)
Interval interval_join(Interval a, Interval b) {
    if (a.is_bottom) return b;
    if (b.is_bottom) return a;
    int min_v = (a.min_val < b.min_val) ? a.min_val : b.min_val;
    int max_v = (a.max_val > b.max_val) ? a.max_val : b.max_val;
    return make_interval(min_v, max_v);
}

// Оператор розширення (Widening) для примусової зупинки циклів
Interval interval_widen(Interval prev, Interval next) {
    if (prev.is_bottom) return next;
    if (next.is_bottom) return prev;
    int min_v = (next.min_val < prev.min_val) ? NEG_INF : prev.min_val;
    int max_v = (next.max_val > prev.max_val) ? INF : prev.max_val;
    return make_interval(min_v, max_v);
}

// Оператор звуження (Narrowing) для повернення точності
Interval interval_narrow(Interval prev, Interval next) {
    if (prev.is_bottom || next.is_bottom) return make_bottom();
    int min_v = (prev.min_val == NEG_INF) ? next.min_val : prev.min_val;
    int max_v = (prev.max_val == INF) ? next.max_val : prev.max_val;
    return make_interval(min_v, max_v);
}

// Перетин інтервалів (для врахування умов розгалуження)
Interval interval_intersect(Interval a, Interval b) {
    if (a.is_bottom || b.is_bottom) return make_bottom();
    int min_v = (a.min_val > b.min_val) ? a.min_val : b.min_val;
    int max_v = (a.max_val < b.max_val) ? a.max_val : b.max_val;
    return make_interval(min_v, max_v);
}

// Абстрактне додавання інтервалів
Interval interval_add(Interval a, Interval b) {
    if (a.is_bottom || b.is_bottom) return make_bottom();
    int min_v = (a.min_val == NEG_INF || b.min_val == NEG_INF) ? NEG_INF : a.min_val + b.min_val;
    int max_v = (a.max_val == INF || b.max_val == INF) ? INF : a.max_val + b.max_val;
    return make_interval(min_v, max_v);
}

// Перевірка, чи містить інтервал нуль
bool interval_contains_zero(Interval iv) {
    if (iv.is_bottom) return false;
    return (iv.min_val <= 0 && iv.max_val >= 0);
}

void print_interval(const char* name, Interval iv) {
    if (iv.is_bottom) {
        printf("%s: ⊥ (недосяжний)\n", name);
        return;
    }
    printf("%s: [", name);
    if (iv.min_val == NEG_INF) printf("-INF");
    else printf("%d", iv.min_val);
    printf(", ");
    if (iv.max_val == INF) printf("+INF");
    else printf("%d", iv.max_val);
    printf("]\n");
}

int main(void) {
    // Аналіз циклу:
    // int x = 1;
    // while (x < 100) { x = x + 2; }
    // int res = 1000 / x;

    Interval x = make_interval(1, 1);
    printf("Початковий стан:\n");
    print_interval("x_0", x);

    // Фаза 1: Пошук нерухомої точки через розширення (Widening)
    Interval guard = make_interval(NEG_INF, 99); // Умова входу в цикл: x < 100
    for (int iter = 1; iter <= 2; ++iter) {
        Interval inside_loop = interval_intersect(x, guard);
        Interval step = make_interval(2, 2);
        Interval x_next = interval_add(inside_loop, step);
        Interval x_joined = interval_join(x, x_next);
        Interval x_widened = interval_widen(x, x_joined);
        
        printf("Ітерація %d (після розширення):\n", iter);
        print_interval("x_loop", x_widened);
        x = x_widened;
    }

    // Фаза 2: Звуження (Narrowing) після виходу з циклу (умова x >= 100)
    Interval exit_guard = make_interval(100, INF);
    Interval x_exit = interval_intersect(x, exit_guard);
    printf("Стан після виходу з циклу (зі звуженням):\n");
    print_interval("x_exit", x_exit);

    if (!interval_contains_zero(x_exit)) {
        printf("Висновок: операція 1000 / x є ГАРАНТОВАНО БЕЗПЕЧНОЮ (0 не входить в інтервал)\n");
    } else {
        printf("Попередження: можливе ділення на нуль!\n");
    }

    return 0;
}
