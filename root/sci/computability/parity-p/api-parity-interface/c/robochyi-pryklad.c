#include <stdio.h>
#include <stdlib.h>
#include "parity_oracle.h"

int main(void) {
    parity_oracle_ctx_t* ctx = NULL;
    parity_status_t st = parity_oracle_create(&ctx, PARITY_FLAG_USE_GAUSS | PARITY_FLAG_COMP_CACHE);
    if (st != PARITY_SUCCESS) {
        fprintf(stderr, "Помилка ініціалізації оракула: %d\n", st);
        return 1;
    }

    /* Задаємо булеву формулу: (x1 OR x2) AND (NOT x1 OR x3) */
    int32_t clauses[] = { 1, 2, 0,  -1, 3, 0 };
    parity_formula_t formula = {
        .num_vars = 3,
        .num_clauses = 2,
        .clause_data = clauses,
        .clause_data_len = 6
    };

    uint8_t parity = 0;
    st = parity_oracle_query_sat(ctx, &formula, &parity);
    if (st == PARITY_SUCCESS) {
        printf("Результат ⊕P оракула: %u (%s)\n",
               parity, parity ? "НЕПАРНА" : "ПАРНА");
    } else {
        printf("Помилка виконання запиту: %d\n", st);
    }

    /* Створення та перевірка рангу бітової матриці 2x2 */
    gf2_matrix_t* mat = NULL;
    if (gf2_matrix_create(&mat, 2, 2) == PARITY_SUCCESS) {
        gf2_matrix_set_bit(mat, 0, 0, true);
        gf2_matrix_set_bit(mat, 0, 1, true);
        gf2_matrix_set_bit(mat, 1, 0, false);
        gf2_matrix_set_bit(mat, 1, 1, true);

        size_t rank = 0;
        if (gf2_matrix_rank(mat, &rank) == PARITY_SUCCESS) {
            printf("Ранг матриці над GF(2): %zu\n", rank);
        }
        gf2_matrix_free(mat);
    }

    parity_oracle_destroy(ctx);
    return 0;
}
