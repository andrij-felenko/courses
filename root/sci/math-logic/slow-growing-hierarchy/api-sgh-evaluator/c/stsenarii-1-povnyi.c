#include "sgh_engine.h"
#include <stdio.h>
#include <inttypes.h>

void run_c_example(void) {
    /* 1. Створення доданків */
    OrdinalNode *term1 = ord_create_omega_term(ord_create_const(2), 3); /* w^2 * 3 */
    OrdinalNode *term2 = ord_create_omega_term(ord_create_const(1), 4); /* w^1 * 4 */
    OrdinalNode *term3 = ord_create_const(5);                           /* 5 */

    /* 2. Агрегація в суму Кантора */
    OrdinalNode *sum = ord_create_sum();
    ord_sum_append(sum, term1);
    ord_sum_append(sum, term2);
    ord_sum_append(sum, term3);

    /* 3. Обчислення значення G_alpha(n) для n = 4 */
    uint64_t n = 4;
    uint64_t result = sgh_eval_homomorphism(sum, n);
    printf("G_alpha(%" PRIu64 ") = %" PRIu64 "\n", n, result);
    /* Очікуваний результат: 4^2 * 3 + 4 * 4 + 5 = 16 * 3 + 16 + 5 = 48 + 16 + 5 = 69 */

    /* 4. Вивільнення пам'яті всього дерева */
    ord_free(sum);
}
