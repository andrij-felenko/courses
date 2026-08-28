#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_SUBSETS 64
#define MAX_ELEMENTS 64

/* Структура представлення підмножини */
typedef struct {
    uint64_t mask;  /* Бітова маска елементів універсуму */
    double cost;    /* Вартість підмножини w(S) */
    int id;         /* Унікальний ідентифікатор */
} Subset;

/* Структура результату розв'язання */
typedef struct {
    int count;
    int selected_ids[MAX_SUBSETS];
    double total_cost;
} Solution;

/* Жадібний алгоритм покриття множини на бітових масках */
Solution greedy_set_cover(const Subset* subsets, int m, uint64_t universe_mask) {
    Solution sol;
    sol.count = 0;
    sol.total_cost = 0.0;

    uint64_t covered = 0;

    while (covered != universe_mask) {
        int best_idx = -1;
        double best_ratio = 1e18;
        int max_new_covered = 0;

        for (int i = 0; i < m; ++i) {
            /* Виділяємо елементи, які ще не були покриті раніше */
            uint64_t newly_covered = subsets[i].mask & (~covered);
            /* Апаратний підрахунок кількості нових елементів */
            int new_count = __builtin_popcountll(newly_covered);

            if (new_count > 0) {
                double ratio = subsets[i].cost / (double)new_count;
                if (ratio < best_ratio) {
                    best_ratio = ratio;
                    best_idx = i;
                    max_new_covered = new_count;
                }
            }
        }

        /* Якщо жодна множина не дає нових елементів — універсум непокривний */
        if (best_idx == -1) {
            break;
        }

        sol.selected_ids[sol.count++] = subsets[best_idx].id;
        sol.total_cost += subsets[best_idx].cost;
        covered |= subsets[best_idx].mask;
    }

    return sol;
}

/* Рекурсивне ядро методу гілок і меж */
static void branch_and_bound_rec(
    const Subset* subsets, int m, uint64_t universe_mask,
    int current_idx, uint64_t current_covered, double current_cost,
    int current_selected[], int current_count,
    Solution* best_sol
) {
    /* Відсікання: якщо поточна накопичена вартість вже гірша за відомий рекорд */
    if (current_cost >= best_sol->total_cost) {
        return;
    }

    /* Базовий випадок: універсум повністю закрито */
    if (current_covered == universe_mask) {
        best_sol->total_cost = current_cost;
        best_sol->count = current_count;
        memcpy(best_sol->selected_ids, current_selected, sizeof(int) * current_count);
        return;
    }

    /* Якщо всі підмножини вичерпано, але універсум не закрито */
    if (current_idx >= m) {
        return;
    }

    /* Гілка 1: Спробувати включити поточну підмножину (якщо вона корисна) */
    uint64_t newly = subsets[current_idx].mask & (~current_covered);
    if (newly > 0) {
        current_selected[current_count] = subsets[current_idx].id;
        branch_and_bound_rec(
            subsets, m, universe_mask,
            current_idx + 1,
            current_covered | subsets[current_idx].mask,
            current_cost + subsets[current_idx].cost,
            current_selected, current_count + 1,
            best_sol
        );
    }

    /* Гілка 2: Пропустити поточну підмножину */
    branch_and_bound_rec(
        subsets, m, universe_mask,
        current_idx + 1,
        current_covered,
        current_cost,
        current_selected, current_count,
        best_sol
    );
}

/* Зовнішній інтерфейс точного розв'язувача */
Solution exact_set_cover(const Subset* subsets, int m, uint64_t universe_mask) {
    Solution best_sol;
    best_sol.count = 0;
    best_sol.total_cost = 1e18;

    int current_selected[MAX_SUBSETS];
    branch_and_bound_rec(
        subsets, m, universe_mask,
        0, 0, 0.0,
        current_selected, 0,
        &best_sol
    );

    return best_sol;
}

int main(void) {
    /* 10 елементів універсуму: біти від 0 до 9 */
    uint64_t universe = (1ULL << 10) - 1;

    Subset subsets[] = {
        { .id = 1, .cost = 4.0, .mask = 0b0000011111 }, /* e1..e5 */
        { .id = 2, .cost = 5.0, .mask = 0b0000100101 }, /* e1, e3, e6 */
        { .id = 3, .cost = 6.0, .mask = 0b0011001010 }, /* e2, e4, e7, e8 */
        { .id = 4, .cost = 3.0, .mask = 0b0011101000 }, /* e4, e6, e7, e8 */
        { .id = 5, .cost = 4.0, .mask = 0b1100010010 }, /* e2, e5, e9, e10 */
        { .id = 6, .cost = 4.0, .mask = 0b0100010000 }  /* e5, e9 */
    };
    int m = sizeof(subsets) / sizeof(subsets[0]);

    Solution greedy = greedy_set_cover(subsets, m, universe);
    printf("=== Жадібний розв'язок (C) ===\n");
    printf("Вартість: %.2f, Підмножин: %d\nПідмножини ID: ", greedy.total_cost, greedy.count);
    for (int i = 0; i < greedy.count; ++i) printf("S%d ", greedy.selected_ids[i]);
    printf("\n\n");

    Solution exact = exact_set_cover(subsets, m, universe);
    printf("=== Точний розв'язок Branch & Bound (C) ===\n");
    printf("Вартість: %.2f, Підмножин: %d\nПідмножини ID: ", exact.total_cost, exact.count);
    for (int i = 0; i < exact.count; ++i) printf("S%d ", exact.selected_ids[i]);
    printf("\n");

    return 0;
}
