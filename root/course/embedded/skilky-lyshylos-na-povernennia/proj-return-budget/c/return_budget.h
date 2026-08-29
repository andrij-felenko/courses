#ifndef RETURN_BUDGET_H
#define RETURN_BUDGET_H

#include <stdbool.h>
#include <stdint.h>

/*
 * Оцінювач енергетичного бюджету повернення (Return Budget Estimator).
 *
 * Модуль не виділяє пам'яті: увесь стан живе в return_budget_handle_t,
 * який заводить викликач — статично або на стеку навігаційної задачі.
 * Усі обчислення — у float32 (апаратний FPU мікроконтролера).
 */

/* Коди повернення функцій модуля */
typedef enum {
    RETURN_OK                    = 0,
    RETURN_ERR_INVALID_CONFIG    = -1,  /* нульовий вказівник або несумісна конфігурація */
    RETURN_ERR_INVALID_TELEMETRY = -2,  /* NaN/inf або від'ємні величини в телеметрії */
    RETURN_ERR_CROSSWIND_LIMIT   = -3,  /* бокова складова вітру ≥ повітряної швидкості */
    RETURN_ERR_HEADWIND_TOO_HIGH = -4   /* шляхова швидкість зближення впала до нуля */
} return_status_t;

/* Стан кінцевого автомата рішень */
typedef enum {
    RETURN_STATE_OK              = 0,  /* запасу вистачає з надлишком */
    RETURN_STATE_CAUTION         = 1,  /* точка неповернення поруч */
    RETURN_STATE_RTL_MANDATORY   = 2,  /* повертатися треба негайно */
    RETURN_STATE_EMERGENCY_LAND  = 3   /* повернення вже неможливе — сідати тут */
} return_state_t;

/* Конфігурація планера й батареї (заповнюється один раз під час старту) */
typedef struct {
    /* Обмеження повітряної швидкості */
    float v_air_min_ms;            /* мінімальна безпечна швидкість (запас до звалювання) */
    float v_air_max_ms;            /* максимальна дозволена швидкість */
    float v_best_range_still_ms;   /* швидкість найкращої дальності у штиль */

    /* Поляра потужності: P(V) = c_ind / V + c_par * V^3 + p_avionics_watts */
    float c_ind;                   /* індуктивна складова, Вт·(м/с) */
    float c_par;                   /* паразитна складова, Вт/(м/с)^3 */
    float p_avionics_watts;        /* постійне споживання авіоніки й корисного вантажу */

    /* Набір ешелону повернення й посадка */
    float rtl_safe_altitude_m;     /* безпечна висота маршруту RTL, м AGL */
    float v_climb_ms;              /* вертикальна швидкість набору, м/с */
    float p_climb_watts;           /* потужність у наборі, Вт */
    float p_hover_watts;           /* потужність зависання/глісади, Вт */
    float t_land_maneuver_sec;     /* тривалість посадкового маневру, с */

    /* Запас і згладжування */
    float reserve_margin_ratio;    /* незнижуваний резерв як частка суми складових, напр. 0.25 */
    float filter_time_constant_s;  /* стала часу фільтра 1-го порядку, с */

    /* Батарея */
    float nominal_energy_wh;       /* паспортна ємність пакета, Вт·год */
    float cell_v_cutoff;           /* напруга відсічки на банку, В */
    uint8_t cell_count;            /* кількість послідовних банок */
} return_config_t;

/* Зріз телеметрії на момент розрахунку */
typedef struct {
    float pos_current_ned[3];   /* поточна позиція в локальній NED, м */
    float pos_home_ned[3];      /* точка Home у тій самій NED, м */
    float wind_ned[2];          /* ВЕКТОР ШВИДКОСТІ повітря (куди дме), м/с: north, east */
    float voltage_v;            /* напруга пакета під поточним навантаженням, В */
    float r_internal_ohms;      /* внутрішній опір пакета, Ом */
    float energy_remaining_wh;  /* залишок за кулонометром, Вт·год */
    bool airspeed_synthetic;    /* true — трубка Піто втрачена, EKF дає синтетичну швидкість */
} return_telemetry_t;

/* Результат одного розрахунку */
typedef struct {
    float distance_to_home_m;
    float time_to_home_sec;
    float v_air_optimal_ms;        /* оптимальна повітряна швидкість повернення */
    float v_ground_ret_ms;         /* шляхова швидкість зближення з базою */
    float wca_rad;                 /* кут випередження вітру */

    float e_cruise_wh;             /* горизонтальний переліт */
    float e_climb_wh;              /* набір безпечного ешелону */
    float e_land_wh;               /* посадковий маневр */
    float e_reserve_wh;            /* гарантований запас */
    float e_return_total_wh;       /* повна вартість повернення ПІСЛЯ фільтра */

    float projected_sag_voltage_v; /* прогноз напруги під струмом повернення */
    float e_usable_compensated_wh; /* залишок після відсікання недосяжної ємності */
    float energy_margin_ratio;     /* (usable − return) / usable */

    return_state_t state;
    bool rtl_mandatory;            /* автопілот мусить негайно піти додому */
} return_budget_result_t;

/* Стан оцінювача між викликами (фільтр + FSM) */
typedef struct {
    return_config_t config;
    float filtered_e_return_wh;
    return_state_t current_state;
    bool initialized;
} return_budget_handle_t;

/* Перевіряє конфігурацію й обнуляє стан. RETURN_OK або RETURN_ERR_INVALID_CONFIG. */
int32_t return_budget_init(return_budget_handle_t* handle, const return_config_t* config);

/* Скидає фільтр і FSM, не чіпаючи конфігурацію (перед новим польотом). */
void return_budget_reset(return_budget_handle_t* handle);

/*
 * Один крок оцінювача. dt_sec — час від попереднього виклику (стала часу фільтра
 * рахується від нього, тож частота виклику може плавати).
 * Повертає RETURN_OK або від'ємний код; out_result заповнюється завжди, коли
 * вказівники дійсні, — у полях state/rtl_mandatory лежить рішення навіть для помилки.
 */
int32_t return_budget_update(return_budget_handle_t* handle,
                             const return_telemetry_t* telem,
                             float dt_sec,
                             return_budget_result_t* out_result);

/* Коротка назва стану для журналу й MAVLink-повідомлень. */
const char* return_budget_state_name(return_state_t state);

#endif /* RETURN_BUDGET_H */
