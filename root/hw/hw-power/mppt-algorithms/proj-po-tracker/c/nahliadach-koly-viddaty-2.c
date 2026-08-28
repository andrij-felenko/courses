#define REG_SIGN     (+1)   // напрям «побільшити D → підняти вихід»: під плату
#define REG_DEAD_MV   50
#define REG_DEAD_MA   40

static void regulate_cv(uint16_t vbatt_mv) {           // тримати напругу
    int32_t e = (int32_t)V_BATT_FULL_MV - (int32_t)vbatt_mv;
    if (e >  REG_DEAD_MV) duty = clamp_duty((int32_t)duty + REG_SIGN);
    if (e < -REG_DEAD_MV) duty = clamp_duty((int32_t)duty - REG_SIGN);
    pwm_set_duty(duty);
}
static void regulate_cc(uint16_t ibatt_ma) {           // тримати струм
    int32_t e = (int32_t)I_BATT_LIMIT_MA - (int32_t)ibatt_ma;
    if (e >  REG_DEAD_MA) duty = clamp_duty((int32_t)duty + REG_SIGN);
    if (e < -REG_DEAD_MA) duty = clamp_duty((int32_t)duty - REG_SIGN);
    pwm_set_duty(duty);
}
