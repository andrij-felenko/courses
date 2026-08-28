// Калібрування за двома точками. Пари виміряні раз і збережені (напр. у NVS/flash).
//   (code_lo, V_LO) і (code_hi, V_HI) — сирий код і ВІДОМА напруга в мВ.
typedef struct { int32_t k_num, k_den, b_mv; } adc_cal_t;   // k як дріб, щоб без float

void adc_cal_build(adc_cal_t *c, int32_t code_lo, int32_t V_LO,
                                  int32_t code_hi, int32_t V_HI) {
    c->k_num = V_HI - V_LO;            // приріст напруги
    c->k_den = code_hi - code_lo;      // приріст коду
    c->b_mv  = V_LO - (c->k_num * code_lo) / c->k_den;   // зсув: де пряма січе нуль коду
}

int32_t adc_cal_apply(const adc_cal_t *c, int32_t code) {
    return (c->k_num * code) / c->k_den + c->b_mv;       // сирий код → калібровані мВ
}
