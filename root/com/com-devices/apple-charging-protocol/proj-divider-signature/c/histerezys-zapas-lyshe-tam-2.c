typedef enum { SRC_UNKNOWN, SRC_500MA, SRC_1A, SRC_2A1, SRC_2A4 } src_class_t;

static src_class_t class_of(lvl_t dp, lvl_t dm)
{
    if (dp == LVL_2V0 && dm == LVL_2V0) return SRC_500MA;
    if (dp == LVL_2V0 && dm == LVL_2V7) return SRC_1A;
    if (dp == LVL_2V7 && dm == LVL_2V0) return SRC_2A1;
    if (dp == LVL_2V7 && dm == LVL_2V7) return SRC_2A4;
    return SRC_UNKNOWN;
}

/* Чи тримається ще той клас, який ми колись прийняли. */
static bool class_still_holds(src_class_t c, int dp_mv, int dm_mv)
{
    lvl_t dp, dm;
    switch (c) {
    case SRC_500MA: dp = LVL_2V0; dm = LVL_2V0; break;
    case SRC_1A:    dp = LVL_2V0; dm = LVL_2V7; break;
    case SRC_2A1:   dp = LVL_2V7; dm = LVL_2V0; break;
    case SRC_2A4:   dp = LVL_2V7; dm = LVL_2V7; break;
    default:        return false;
    }
    return lvl_holds(dp, dp_mv) && lvl_holds(dm, dm_mv);
}
