/* Специфіковані вікна. Вхід у клас — ТІЛЬКИ за ними. */
#define W2V0_LO  1900
#define W2V0_HI  2100
#define W2V7_LO  2570
#define W2V7_HI  2840

/* Запас — лише на ВИХІД. Нічия земля між вікнами завширшки 470 мВ, тож
   60 мВ з кожного боку туди вміщаються, не перетинаючись. */
#define GUARD_MV 60

typedef enum { LVL_NONE, LVL_2V0, LVL_2V7 } lvl_t;

/* Увійти в рівень можна лише за чистим вікном. */
static lvl_t lvl_enter(int mv)
{
    if (mv >= W2V0_LO && mv <= W2V0_HI) return LVL_2V0;
    if (mv >= W2V7_LO && mv <= W2V7_HI) return LVL_2V7;
    return LVL_NONE;
}

/* А втриматися в ньому — за вікном плюс запас. Асиметрія й є гістерезис. */
static bool lvl_holds(lvl_t l, int mv)
{
    switch (l) {
    case LVL_2V0: return mv >= W2V0_LO - GUARD_MV && mv <= W2V0_HI + GUARD_MV;
    case LVL_2V7: return mv >= W2V7_LO - GUARD_MV && mv <= W2V7_HI + GUARD_MV;
    default:      return false;
    }
}
