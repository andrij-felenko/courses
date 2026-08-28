#include <stdbool.h>

typedef enum { SRC_UNKNOWN, SRC_500MA, SRC_1A, SRC_2A1, SRC_2A4 } src_class_t;

static bool in_window(int mv, int lo, int hi) { return mv >= lo && mv <= hi; }

#define IS_2V0(mv)  in_window((mv), 1900, 2100)
#define IS_2V7(mv)  in_window((mv), 2570, 2840)

/* mv_dp, mv_dm — уже виміряні АЦП мілівольти на лініях D+ і D− */
src_class_t classify(int mv_dp, int mv_dm)
{
    if (IS_2V0(mv_dp) && IS_2V0(mv_dm)) return SRC_500MA;  /* слабке джерело  */
    if (IS_2V0(mv_dp) && IS_2V7(mv_dm)) return SRC_1A;     /* Divider 1, 5 Вт */
    if (IS_2V7(mv_dp) && IS_2V0(mv_dm)) return SRC_2A1;    /* Divider 2, 10 Вт*/
    if (IS_2V7(mv_dp) && IS_2V7(mv_dm)) return SRC_2A4;    /* Divider 3, 12 Вт*/
    return SRC_UNKNOWN;                                    /* чужий діалект   */
}
