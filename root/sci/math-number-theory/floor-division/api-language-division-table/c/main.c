#include <stdint.h>
#include <stdbool.h>
#include <limits.h>

// Безпечна перевірка ділення C99 перед виконанням IDIV
bool is_safe_division_s32(int32_t a, int32_t b) {
    if (b == 0) return false;
    if (a == INT32_MIN && b == -1) return false;
    return true;
}
