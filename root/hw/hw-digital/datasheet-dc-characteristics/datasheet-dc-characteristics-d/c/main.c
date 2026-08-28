// Межі з DC-таблиці приймача (74HC на 4.5 В), у мілівольтах — цілі, без float.
#define VIH_MIN_MV   3150   // вхід читає «1» від 3.15 В
#define VIL_MAX_MV   1350   // вхід читає «0» до 1.35 В

typedef enum { LVL_LOW, LVL_HIGH, LVL_FORBIDDEN } logic_level_t;

// Класифікувати виміряну на піні напругу за порогами приймача.
logic_level_t classify_level(uint16_t v_mv)
{
    if (v_mv >= VIH_MIN_MV) return LVL_HIGH;       // впевнена «1»
    if (v_mv <= VIL_MAX_MV) return LVL_LOW;        // впевнений «0»
    return LVL_FORBIDDEN;                          // заборонена зона — тривога
}

// Перевірити, чи «1» драйвера дотягується до порога приймача із запасом.
bool high_level_ok(uint16_t voh_driver_mv, uint16_t noise_budget_mv)
{
    // потрібно: VOH(драйвера) − VIH(приймача) ≥ бюджет шуму
    return (voh_driver_mv >= VIH_MIN_MV) &&
           (voh_driver_mv - VIH_MIN_MV >= noise_budget_mv);
}
