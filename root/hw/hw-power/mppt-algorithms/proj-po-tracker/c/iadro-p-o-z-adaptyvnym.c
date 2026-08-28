// ── Ядро Perturb & Observe з адаптивним кроком ─────────────────────────────
#define DUTY_MIN      80u     // не даємо перетворювачу впасти в нуль
#define DUTY_MAX     900u     // і не заганяємо в насичення (одиниці таймера)
#define STEP_MIN       1u     // найдрібніший крок біля піка
#define STEP_MAX      24u     // найбільший крок здалеку
#define DP_DEADBAND  30000    // мкВт (30 мВт): поріг шуму — менше не реагуємо
#define STEP_GAIN_SH   14     // |ΔP| >> 14 → крок; коефіцієнт підбирають під плату

static uint16_t duty   = DUTY_MIN;
static int32_t  p_prev = 0;
static int8_t   dir    = +1;

static uint16_t clamp_duty(int32_t d) {
    if (d < DUTY_MIN) return DUTY_MIN;
    if (d > DUTY_MAX) return DUTY_MAX;
    return (uint16_t)d;
}

// Крок пропорційний |ΔP|, затиснутий у [STEP_MIN, STEP_MAX].
static uint16_t adaptive_step(int32_t dp_abs) {
    uint32_t s = (uint32_t)dp_abs >> STEP_GAIN_SH;
    if (s < STEP_MIN) s = STEP_MIN;
    if (s > STEP_MAX) s = STEP_MAX;
    return (uint16_t)s;
}

// Один крок рішення P&O. Викликати ЛИШЕ після влягання й на свіжому,
// усередненому за вікно вимірі — інакше рішення випадкове (див. нижче).
static void po_decide(const meas_t *m) {
    int32_t dp = m->puw - p_prev;

    if (dp < -DP_DEADBAND)       // потужність ВІДЧУТНО впала —
        dir = -dir;              //   минулий крок був не туди, розвернутись
    // |dp| ≤ DP_DEADBAND — у межах шуму, напрям лишаємо (інакше пульсації
    //   самі клацали б dir туди-сюди на піку).

    uint16_t step = adaptive_step(dp < 0 ? -dp : dp);
    duty = clamp_duty((int32_t)duty + dir * (int32_t)step);
    pwm_set_duty(duty);          // ЦЕ і є збурення D

    p_prev = m->puw;             // запам'ятати для наступного порівняння
}
