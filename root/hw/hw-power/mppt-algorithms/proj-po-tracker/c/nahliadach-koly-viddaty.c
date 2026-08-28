// ── Наглядач: коли MPPT має відпустити кермо ───────────────────────────────
#define I_BATT_LIMIT_MA  3000    // паспортний струм заряду
#define V_BATT_FULL_MV  14200    // поріг CV (приклад: 4S LiFePO4)
#define V_FULL_HYST_MV    200     // гістерезис повернення в MPPT з CV
#define I_LIMIT_HYST_MA   150     // гістерезис повернення в MPPT з CC

typedef enum { MODE_MPPT, MODE_CC, MODE_CV } mode_t;
static mode_t mode = MODE_MPPT;

static void supervisor_update(uint16_t vbatt_mv, uint16_t ibatt_ma) {
    switch (mode) {
    case MODE_MPPT:
        if      (vbatt_mv >= V_BATT_FULL_MV)   mode = MODE_CV;   // напруга повна
        else if (ibatt_ma >= I_BATT_LIMIT_MA)  mode = MODE_CC;   // струм на ліміті
        break;
    case MODE_CC:
        if      (vbatt_mv >= V_BATT_FULL_MV)   mode = MODE_CV;
        else if (ibatt_ma <  I_BATT_LIMIT_MA - I_LIMIT_HYST_MA) mode = MODE_MPPT;
        break;
    case MODE_CV:
        if (vbatt_mv < V_BATT_FULL_MV - V_FULL_HYST_MV) mode = MODE_MPPT;
        break;
    }
}
