#include <stdint.h>
#include <stdbool.h>

// ── Межі з DC-таблиць, у ЦІЛИХ мілівольтах (звірено з даташитами) ──
// Драйвер: 3.3 В LVCMOS, найгірший кут VCC = 3.0 В.
#define DRV_VOH_MIN_MV   2800   // «1» майже без струму (VCC − 0.2 В)
#define DRV_VOL_MAX_MV    400   // «0» під помірним струмом (рядок IOL = 12 мА)

// Приймач А: 74HCT — входи ТТЛ-сумісні.
#define HCT_VIH_MIN_MV   2000   // читає «1» від 2.0 В
#define HCT_VIL_MAX_MV    800   // читає «0» до 0.8 В

// Приймач Б: 74HC на 4.5 В — входи чистого КМОН (0.7/0.3 · VCC).
#define HC_VIH_MIN_MV    3150   // читає «1» лише від 3.15 В
#define HC_VIL_MAX_MV    1350   // читає «0» до 1.35 В

// Скільки шуму лінія має проковтнути, перш ніж помилитись (бюджет запасу).
#define NOISE_BUDGET_MV   200

typedef enum { LVL_LOW, LVL_HIGH, LVL_FORBIDDEN } logic_level_t;

// Класифікувати ВИМІРЯНУ напругу за порогами КОНКРЕТНОГО приймача.
logic_level_t classify_level(uint16_t v_mv,
                             uint16_t vil_max_mv, uint16_t vih_min_mv)
{
    if (v_mv >= vih_min_mv) return LVL_HIGH;      // впевнена «1»
    if (v_mv <= vil_max_mv) return LVL_LOW;       // впевнений «0»
    return LVL_FORBIDDEN;                         // заборонена зона — тривога
}

// Результат звірки одного стику: проходить + запас у кожен бік.
typedef struct {
    bool     high_ok;         // «1» драйвера дотягується до VIH приймача?
    bool     low_ok;          // «0» драйвера нижче за VIL приймача?
    int16_t  high_margin_mv;  // VOH(драйв.) − VIH(прийм.); від'ємне = провал
    int16_t  low_margin_mv;   // VIL(прийм.) − VOL(драйв.); від'ємне = провал
} link_check_t;

// Перевірка стику НАВХРЕСТ: рівні драйвера проти порогів приймача.
// Усе в мВ, знаковий int16 — щоб від'ємний запас (провал) було видно.
link_check_t check_link(uint16_t drv_voh_mv, uint16_t drv_vol_mv,
                        uint16_t rx_vih_mv,  uint16_t rx_vil_mv,
                        uint16_t budget_mv)
{
    link_check_t r;
    // «1»: наскільки VOH драйвера перевищує поріг VIH приймача.
    r.high_margin_mv = (int16_t)drv_voh_mv - (int16_t)rx_vih_mv;
    r.high_ok = (r.high_margin_mv >= (int16_t)budget_mv);
    // «0»: наскільки VOL драйвера нижче за поріг VIL приймача.
    r.low_margin_mv  = (int16_t)rx_vil_mv - (int16_t)drv_vol_mv;
    r.low_ok  = (r.low_margin_mv >= (int16_t)budget_mv);
    return r;
}

// ── Приклад застосування: звіряємо обидва варіанти приймача ──
void self_test_link(void)
{
    // Варіант А: 3.3 В LVCMOS → 74HCT.
    link_check_t a = check_link(DRV_VOH_MIN_MV, DRV_VOL_MAX_MV,
                                HCT_VIH_MIN_MV, HCT_VIL_MAX_MV,
                                NOISE_BUDGET_MV);
    // a.high_ok == true,  a.high_margin_mv == 2800 − 2000 = +800 мВ
    // a.low_ok  == true,  a.low_margin_mv  ==  800 − 400  = +400 мВ

    // Варіант Б: той самий драйвер → 74HC.
    link_check_t b = check_link(DRV_VOH_MIN_MV, DRV_VOL_MAX_MV,
                                HC_VIH_MIN_MV, HC_VIL_MAX_MV,
                                NOISE_BUDGET_MV);
    // b.high_ok == false, b.high_margin_mv == 2800 − 3150 = −350 мВ  ← ПРОВАЛ!
    // b.low_ok  == true,  b.low_margin_mv  == 1350 − 400  = +950 мВ

    if (!b.high_ok) {
        // «1» не проходить: тривога ще на етапі самотесту, до збою в полі.
        raise_fault(FAULT_LEVEL_MISMATCH, b.high_margin_mv);
    }
}
