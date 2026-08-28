#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Безрозгалужена версія оновлення лічильника */
void majority_update_branchless(int32_t *candidate, int32_t *count, int32_t x) {
    /* Якщо count == 0, кандидат заміщується на x */
    int32_t is_zero = (*count == 0);
    *candidate = is_zero ? x : *candidate;
    
    /* delta = +1 якщо x == candidate, інакше -1 */
    int32_t is_match = (*candidate == x);
    int32_t delta = (is_match << 1) - 1; /* 1 -> +1, 0 -> -1 */
    
    /* Якщо count було 0, новий count стає 1 */
    *count = is_zero ? 1 : (*count + delta);
}

int32_t find_candidate_branchless(const int32_t *data, size_t size) {
    int32_t candidate = 0;
    int32_t count = 0;

    for (size_t i = 0; i < size; ++i) {
        int32_t x = data[i];
        int32_t is_zero = (count == 0);
        candidate = is_zero ? x : candidate;
        count = is_zero ? 1 : (count + ((candidate == x) ? 1 : -1));
    }

    return candidate;
}
