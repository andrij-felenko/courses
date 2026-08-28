#include <stdio.h>
#include <assert.h>

void demo_client_usage(void) {
    /* Створення ординала epsilon_0 = phi(1, 0) */
    OrdinalNode* eps0 = ord_veblen(ord_finite(1), ord_zero());

    /* Створення ординала omega = phi(0, 1) */
    OrdinalNode* omega = ord_veblen(ord_zero(), ord_finite(1));

    /* Обчислення суми: omega + epsilon_0 (повинно дати epsilon_0 через поглинання) */
    OrdinalNode* sum = ord_add(ord_clone(omega), ord_clone(eps0));

    /* Перевірка еквівалентності */
    assert(ord_cmp(sum, eps0) == 0);

    ord_free(eps0);
    ord_free(omega);
    ord_free(sum);
}
