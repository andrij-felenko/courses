/* Реалізація мовою C: класична структура з ручним керуванням пам'яттю */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int64_t* pref;
    size_t size;
} PrefixSum1D;

/* Побудова префіксного масиву з виділенням N + 1 елементів */
bool prefix_sum_1d_init(PrefixSum1D* ps, const int32_t* arr, size_t n) {
    if (!ps || (!arr && n > 0)) return false;
    
    ps->pref = (int64_t*)malloc((n + 1) * sizeof(int64_t));
    if (!ps->pref) {
        ps->size = 0;
        return false;
    }
    
    ps->size = n;
    ps->pref[0] = 0;
    for (size_t i = 0; i < n; ++i) {
        ps->pref[i + 1] = ps->pref[i] + (int64_t)arr[i];
    }
    return true;
}

/* Запит суми на відрізку [l, r] в 0-вказаній індексації (включно) */
int64_t prefix_sum_1d_query(const PrefixSum1D* ps, size_t l, size_t r) {
    if (!ps || !ps->pref || l > r || r >= ps->size) {
        return 0; /* Обробка межевих помилок */
    }
    return ps->pref[r + 1] - ps->pref[l];
}

/* Звільнення пам'яті */
void prefix_sum_1d_free(PrefixSum1D* ps) {
    if (ps && ps->pref) {
        free(ps->pref);
        ps->pref = NULL;
        ps->size = 0;
    }
}
