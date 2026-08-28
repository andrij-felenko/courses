#include <math.h>                          /* fabs */

#define CHECK_NEAR(actual, expected, tol)                                  \
    do {                                                                   \
        double tt_a = (actual), tt_e = (expected), tt_t = (tol);           \
        double tt_d = fabs(tt_a - tt_e);                                   \
        if (!(tt_d <= tt_t)) {                                             \
            snprintf(tt_msg, sizeof tt_msg,                                \
                     "%s: маємо %.17g, чекали %.17g (±%g), розбіг %g",     \
                     #actual, tt_a, tt_e, tt_t, tt_d);                     \
            tt_fail(__FILE__, __LINE__);                                   \
        }                                                                  \
    } while (0)
