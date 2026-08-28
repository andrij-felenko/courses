typedef enum { BATT_OK, BATT_LOW, BATT_CRITICAL } batt_level_t;

// два пороги × дві межі кожен: нижня — спрацювати, вища — відпустити
#define V_LOW_TRIP   14.0f   // нижче цього — «низька» (додому)
#define V_LOW_CLEAR  14.6f   // вище цього — «низька» скасовується
#define V_CRT_TRIP   13.2f   // нижче цього — «критична» (сідай)
#define V_CRT_CLEAR  13.8f   // вище цього — «критична» скасовується
#define T_HOLD_S     10.0f   // умова має протриматись стільки секунд

static batt_level_t batt_classify(float v) {
    static batt_level_t level = BATT_OK;   // ПАМ'ЯТЬ: що вирішили минулого разу
    static float t_low = 0, t_crt = 0;     // таймери «умова тримається»

    // нагромаджуємо час, поки відповідний поріг пробито; інакше скидаємо
    t_crt = (v < V_CRT_TRIP) ? (t_crt + FSM_DT) : 0.0f;
    t_low = (v < V_LOW_TRIP) ? (t_low + FSM_DT) : 0.0f;

    switch (level) {
    case BATT_OK:
        if (t_crt >= T_HOLD_S)      level = BATT_CRITICAL;
        else if (t_low >= T_HOLD_S) level = BATT_LOW;
        break;
    case BATT_LOW:
        if (t_crt >= T_HOLD_S)      level = BATT_CRITICAL;  // глибше — одразу
        else if (v > V_LOW_CLEAR)   level = BATT_OK;        // відпуск — ЛИШЕ через верхню межу
        break;
    case BATT_CRITICAL:
        // з критичної НЕ повертаємось автоматично: сідання не скасовують
        break;
    }
    return level;
}
