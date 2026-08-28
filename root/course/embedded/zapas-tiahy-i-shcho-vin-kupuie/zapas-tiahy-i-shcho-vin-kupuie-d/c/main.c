#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define GRAVITY 9.81
#define AIR_DENSITY 1.225

typedef struct {
    double mass_kg;              /* Повна злітна маса апарата */
    double frontal_area_m2;      /* Еквівалентна площа міделю */
    double drag_coefficient;     /* Коефіцієнт лобового опору Cd */
    double max_wind_speed_ms;    /* Максимальна швидкість вітру */
    double target_tilt_deg;      /* Розрахунковий кут нахилу */
    double min_climb_accel_ms2;  /* Мінімальне прискорення вгору */
    double pid_reserve_factor;   /* Коефіцієнт запасу на авторитет PID (1.3..1.5) */
    double battery_voltage_v;    /* Номінальна напруга батареї */
    double pwm_frequency_hz;     /* Частота ШІМ регулятора */
    double mosfet_switch_time_s; /* Сумарний час перемикання MOSFET (tr + tf) */
} FlightMissionConfig;

typedef struct {
    double required_twr;         /* Розрахований оптимальний TWR */
    double max_thrust_n;         /* Необхідна сумарна максимальна тяга */
    double max_thrust_kgf;       /* Тяга в кілограмах сили */
    double hover_throttle_pct;   /* Відсоток газу при висінні */
    double hover_duty_cycle;     /* Коефіцієнт заповнення ШІМ D на висінні */
    double ripple_current_factor;/* Множник середньоквадратичного струму пульсацій */
    double esc_switch_loss_w;    /* Оцінка комутаційних втрат одного ключа на висінні */
    bool is_twr_too_low;         /* Прапорець: ризик втрати керованості */
    bool is_twr_excessive;       /* Прапорець: надлишковий TWR (перегрів/нелінійність) */
} OptimizationResult;

OptimizationResult calculate_optimal_twr(const FlightMissionConfig* cfg, double motor_hover_current_a) {
    OptimizationResult res = {0};
    
    /* 1. Аеродинамічний опір при зустрічному вітрі */
    double drag_force = 0.5 * AIR_DENSITY * cfg->drag_coefficient * 
                        cfg->frontal_area_m2 * pow(cfg->max_wind_speed_ms, 2);
    
    /* 2. Необхідні складові сили: вертикальна та горизонтальна */
    double weight_n = cfg->mass_kg * GRAVITY;
    double req_vertical_n = cfg->mass_kg * (GRAVITY + cfg->min_climb_accel_ms2);
    double req_horizontal_n = drag_force;
    
    /* 3. Векторна сума сил під час маневру */
    double vector_thrust_n = sqrt(pow(req_vertical_n, 2) + pow(req_horizontal_n, 2));
    
    /* 4. Максимальна тяга з урахуванням запасу авторитету PID */
    res.max_thrust_n = vector_thrust_n * cfg->pid_reserve_factor;
    res.max_thrust_kgf = res.max_thrust_n / GRAVITY;
    res.required_twr = res.max_thrust_n / weight_n;
    
    /* 5. Точка зависання та коефіцієнт заповнення ШІМ */
    res.hover_throttle_pct = (weight_n / res.max_thrust_n) * 100.0;
    res.hover_duty_cycle = res.hover_throttle_pct / 100.0;
    
    /* 6. Струмові пульсації на конденсаторах: sqrt(D * (1 - D)) */
    double d = res.hover_duty_cycle;
    if (d > 0.0 && d < 1.0) {
        res.ripple_current_factor = sqrt(d * (1.0 - d));
    } else {
        res.ripple_current_factor = 0.0;
    }
    
    /* 7. Комутаційні втрати перемикання MOSFET одного плеча */
    res.esc_switch_loss_w = cfg->pwm_frequency_hz * cfg->battery_voltage_v * 
                            motor_hover_current_a * (cfg->mosfet_switch_time_s / 2.0);
    
    /* 8. Перевірка граничних режимів */
    res.is_twr_too_low = (res.hover_throttle_pct > 60.0) || (res.required_twr < 1.8);
    res.is_twr_excessive = (res.hover_throttle_pct < 18.0) || (res.required_twr > 6.0);
    
    return res;
}
