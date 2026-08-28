#include <stdint.h>

// NARROW — цільовий тип (int8_t), WIDE — тип із запасом (int16_t),
// LO/HI — межі цільового типу.
#define DEFINE_ADD_SAT(NAME, NARROW, WIDE, LO, HI)          \
    static inline NARROW NAME(NARROW a, NARROW b) {         \
        WIDE sum = (WIDE)a + (WIDE)b;                       \
        if (sum < (LO)) sum = (LO);                         \
        if (sum > (HI)) sum = (HI);                         \
        return (NARROW)sum;                                 \
    }

DEFINE_ADD_SAT(add_sat_s8,  int8_t,  int16_t, INT8_MIN,  INT8_MAX)
DEFINE_ADD_SAT(add_sat_s16, int16_t, int32_t, INT16_MIN, INT16_MAX)
DEFINE_ADD_SAT(add_sat_s32, int32_t, int64_t, INT32_MIN, INT32_MAX)
