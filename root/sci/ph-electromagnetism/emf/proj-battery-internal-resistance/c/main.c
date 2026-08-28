#include <stdio.h>
#include <stdbool.h>

/* Структура параметрів джерела живлення */
typedef struct {
    double nominal_emf;       /* Амплітуда ЕРС у вольтах (наприклад, 3.7 В) */
    double internal_r_init;   /* Початковий внутрішній опір у омах (наприклад, 0.15 Ом) */
    double capacity_ah;       /* Ємність акумулятора в ампер-годинах (наприклад, 2.0 А·год) */
    double current_soc;       /* Поточний стан заряду у відсотках (0.0 - 100.0%) */
} battery_t;

/* Структура результату вимірювання кроку */
typedef struct {
    double terminal_voltage;  /* Напруга на клемах, В */
    double current;           /* Струм у колі, А */
    double power_load;        /* Потужність у навантаженні, Вт */
    double power_loss;        /* Втрати на внутрішньому опорі, Вт */
    bool reset_warning;       /* Прапор небезпечного просідання напруги */
} battery_step_result_t;

/* Розрахунок поточного ЕРС з урахуванням кривої розрядки */
static double calculate_emf(const battery_t* bat) {
    double soc_norm = bat->current_soc / 100.0;
    /* Лінійно-апроксимована модель ЕРС Li-ion: від 4.2 В (100%) до 3.0 В (0%) */
    return 3.0 + 1.2 * soc_norm;
}

/* Розрахунок динамічного внутрішнього опору */
static double calculate_internal_r(const battery_t* bat) {
    double soc_norm = bat->current_soc / 100.0;
    /* Зростання опору при розрядці нижче 20% за параболічним законом */
    if (soc_norm < 0.20) {
        double factor = (0.20 - soc_norm) / 0.20;
        return bat->internal_r_init * (1.0 + 3.0 * factor * factor);
    }
    return bat->internal_r_init;
}

/* Крок симуляції розряду під навантаженням R_load на час dt_sec */
battery_step_result_t battery_simulate_step(battery_t* bat, double r_load, double dt_sec) {
    battery_step_result_t res;
    
    double current_emf = calculate_emf(bat);
    double current_r = calculate_internal_r(bat);
    
    /* Струм за законом Ома для повного кола */
    res.current = current_emf / (r_load + current_r);
    
    /* Напруга на клемах під навантаженням */
    res.terminal_voltage = current_emf - res.current * current_r;
    
    /* Потужності */
    res.power_load = res.terminal_voltage * res.current;
    res.power_loss = res.current * res.current * current_r;
    
    /* Поріг скидання контролера (2.85 В) */
    res.reset_warning = (res.terminal_voltage < 2.85);
    
    /* Оновлення стану заряду (SoC) методом Ейлера */
    double discharged_ah = (res.current * dt_sec) / 3600.0;
    bat->current_soc -= (discharged_ah / bat->capacity_ah) * 100.0;
    if (bat->current_soc < 0.0) {
        bat->current_soc = 0.0;
    }
    
    return res;
}
