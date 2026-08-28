#include <stdint.h>
#include <stdbool.h>

// У C99 (Annex J / TC3) запис в одне поле union і читання з іншого є легальним
typedef union {
    float f;
    uint32_t u;
} FloatPunC;

bool is_negative_union_c(float f) {
    FloatPunC pun;
    pun.f = f;
    return (pun.u & 0x80000000u) != 0;
}
