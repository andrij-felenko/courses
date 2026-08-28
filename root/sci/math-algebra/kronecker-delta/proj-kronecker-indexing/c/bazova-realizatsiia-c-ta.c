#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/*
 * Безрозгалужена реалізація символу Кронекера.
 * Використовує булеве порівняння, яке компілятор транслює
 * в інструкцію sete/cmov без умовних стрибків.
 */
static inline int kronecker_delta(size_t i, size_t j) {
    return (i == j) ? 1 : 0;
}

/*
 * Зважений фільтр: повертає значення val, якщо i == j, інакше 0.
 * Дозволяє уникати розгалуження if (i == j) sum += val;
 */
static inline double kronecker_select(size_t i, size_t j, double val) {
    return (double)(i == j) * val;
}
