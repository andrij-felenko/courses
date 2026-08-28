#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

void run_c_parity_workflow(void) {
    /* Побудова виразу Rem(n, 2): n ∸ (2 · (n / 2)) */
    KalmarNode* div_expr = kalmar_make_binop(KALMAR_NODE_DIV, kalmar_make_var(0), kalmar_make_const(2));
    KalmarNode* mul_expr = kalmar_make_binop(KALMAR_NODE_MUL, kalmar_make_const(2), div_expr);
    KalmarNode* rem_expr = kalmar_make_binop(KALMAR_NODE_SUB, kalmar_make_var(0), mul_expr);
    KalmarNode* is_even  = kalmar_make_binop(KALMAR_NODE_SUB, kalmar_make_const(1), rem_expr);

    size_t k = kalmar_compute_tower_height(is_even);
    printf("C API: Verified tower height k = %zu\n", k);

    uint64_t vars[2] = {0};
    KalmarEnvironment env = { .vars = vars, .capacity = 2, .step_count = 0, .step_limit = 1000 };

    bool is_true = false;
    vars[0] = 42;
    if (kalmar_eval_predicate(is_even, &env, &is_true) == KALMAR_OK) {
        printf("Number 42 is %s\n", is_true ? "EVEN" : "ODD");
    }

    kalmar_free_tree(is_even);
}
