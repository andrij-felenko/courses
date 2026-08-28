#include <stdint.h>
#include <stdbool.h>
#include <limits.h>

typedef struct {
    int64_t quot;
    int64_t rem;
} div_result_t;

// Безпечне ділення за підлогою (Floor Division) у стилі Python //
div_result_t floor_div_s64(int64_t a, int64_t b) {
    div_result_t res;
    if (b == 0) {
        res.quot = 0; res.rem = 0; return res;
    }
    // Захист від апаратного переповнення INT64_MIN / -1
    if (a == INT64_MIN && b == -1) {
        res.quot = INT64_MAX; res.rem = 0; return res;
    }

    res.quot = a / b;
    res.rem  = a % b;
    
    // Коригуємо, якщо остача не нульова і знаки a та b відрізняються
    bool has_rem = (res.rem != 0);
    bool diff_signs = ((a < 0) ^ (b < 0));
    
    if (has_rem && diff_signs) {
        res.quot -= 1;
        res.rem  += b;
    }
    return res;
}

// Безпечне евклідове ділення (Euclidean Division) зі строго невід'ємною остачею
div_result_t euclidean_div_s64(int64_t a, int64_t b) {
    div_result_t res;
    if (b == 0) {
        res.quot = 0; res.rem = 0; return res;
    }
    if (a == INT64_MIN && b == -1) {
        res.quot = INT64_MAX; res.rem = 0; return res;
    }

    res.quot = a / b;
    res.rem  = a % b;
    
    if (res.rem < 0) {
        if (b > 0) {
            res.quot -= 1;
            res.rem  += b;
        } else {
            res.quot += 1;
            res.rem  -= b;
        }
    }
    return res;
}
