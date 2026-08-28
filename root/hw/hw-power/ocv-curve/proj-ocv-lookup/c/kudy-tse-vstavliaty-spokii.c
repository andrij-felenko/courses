#define REST_I_MA        30u     // спокою немає, поки |I| більший за це
#define REST_MIN_MS  600000u     // і поки від зняття струму не минуло 10 хв
#define REST_CREEP_01MV   3u     // і поки напруга за хвилину повзе більш ніж на 0.3 мВ

static uint32_t rest_since_ms = 0;
static uint16_t v_minute_ago  = 0;   // оновлює той, хто кличе, раз на хвилину

bool cell_is_at_rest(uint16_t i_ma_abs, uint16_t v_01mv, uint32_t now_ms) {
    if (i_ma_abs > REST_I_MA) { rest_since_ms = now_ms; return false; }
    // Різниця беззнакових коректна й після перевороту лічильника мілісекунд.
    if (now_ms - rest_since_ms < REST_MIN_MS) return false;

    int32_t creep = (int32_t)v_01mv - (int32_t)v_minute_ago;
    if (creep < 0) creep = -creep;
    return creep <= REST_CREEP_01MV;
}
