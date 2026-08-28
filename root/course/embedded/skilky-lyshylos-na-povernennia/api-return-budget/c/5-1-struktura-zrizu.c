typedef struct {
    float pos_current_ned[3];     /* Поточна позиція [Північ, Схід, Вниз], метри */
    float pos_home_ned[3];        /* Позиція точки повернення Home [Північ, Схід, Вниз], метри */
    float wind_ned[2];            /* Вектор горизонтального вітру [North, East], м/с */
    float voltage_v;              /* Поточна напруга батареї під навантаженням, В */
    float current_a;              /* Поточний струм розряду, А */
    float energy_remaining_wh;    /* Оцінка залишкової енергії, Вт·год */
    float soc_ratio;              /* Ступінь заряду (0.0 … 1.0) */
    float r_internal_ohms;        /* Внутрішній опір збірки, Ом */
    float battery_temp_c;         /* Температура акумуляторного блоку, °C */
} return_telemetry_t;
