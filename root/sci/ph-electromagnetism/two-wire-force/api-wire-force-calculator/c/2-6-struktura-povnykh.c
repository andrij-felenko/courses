typedef struct wf_calc_result {
    double peak_current_ka;      /* Амплітуда ударного струму i_th, кА */
    double force_per_meter_kn_m; /* Максимальна динамічна сила на метр F_din, кН/м */
    double total_span_force_kn;  /* Сумарна динамічна сила на весь проліт, кН */
    double bending_moment_nm;    /* Максимальний розрахунковий згинний момент, Н·м */
    double bending_stress_mpa;   /* Виникаюче механічне напруження вигину σ, МПа */
    double insulator_load_kn;    /* Реактивне навантаження на опорний ізолятор, кН */
    double actual_safety_factor; /* Фактичний обрахований коефіцієнт запасу */
    bool is_stress_ok;           /* true = напруження шини не перевищує допустимого */
    bool is_insulator_ok;        /* true = ізолятор витримує механічне навантаження */
    bool is_overall_safe;        /* true = конструкція повністю відповідає нормативам */
} wf_calc_result_t;
