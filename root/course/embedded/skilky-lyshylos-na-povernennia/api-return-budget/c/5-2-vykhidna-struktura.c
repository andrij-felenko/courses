typedef struct {
    float v_air_optimal_ms;       /* Оптимальна повітряна швидкість повернення V_a*, м/с */
    float v_ground_ret_ms;        /* Очікувана шляхова швидкість зближення з базою V_g, м/с */
    float wca_rad;                /* Кут випередження вітру WCA, радіани */
    float distance_to_home_m;     /* Пряма дистанція до домашньої точки, м */
    float time_to_home_sec;       /* Розрахунковий час повернення, с */
    float e_cruise_wh;            /* Енергія горизонтального перельоту проти вітру, Вт·год */
    float e_climb_wh;             /* Енергія набору безпечної висоти RTL, Вт·год */
    float e_land_wh;              /* Енергія процедури посадки, Вт·год */
    float e_reserve_wh;           /* Енергетичний запас на маневри й пориви, Вт·год */
    float e_return_total_wh;      /* Повна необхідна енергія на повернення, Вт·год */
    float e_usable_compensated_wh;/* Фактично доступна корисна енергія (Voltage Sag), Вт·год */
    float projected_sag_voltage_v;/* Прогнозована напруга на клемах при тязі повернення, В */
    float energy_margin_ratio;    /* Відносний залишок: (E_usable - E_return) / E_usable */
    uint8_t state;                /* Стан return_state_t */
    bool rtl_mandatory;           /* true — точка неповернення пройдена, потрібен RTL */
} return_budget_result_t;
