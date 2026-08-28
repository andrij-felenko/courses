#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

typedef enum {
    MSL_LEVEL_1 = 0,
    MSL_LEVEL_2,
    MSL_LEVEL_2A,
    MSL_LEVEL_3,
    MSL_LEVEL_4,
    MSL_LEVEL_5,
    MSL_LEVEL_5A,
    MSL_LEVEL_6
} msl_level_t;

typedef struct {
    msl_level_t level;
    const char* name;
    uint32_t floor_life_hours; /* 0xFFFFFFFF = необмежено */
    double max_temp_c;
    double max_rh_percent;
} msl_spec_t;

static const msl_spec_t MSL_SPECS[] = {
    { MSL_LEVEL_1,  "MSL 1",  UINT32_MAX, 30.0, 85.0 },
    { MSL_LEVEL_2,  "MSL 2",  8760,       30.0, 60.0 }, /* 1 рік */
    { MSL_LEVEL_2A, "MSL 2a", 672,        30.0, 60.0 }, /* 4 тижні */
    { MSL_LEVEL_3,  "MSL 3",  168,        30.0, 60.0 }, /* 7 діб */
    { MSL_LEVEL_4,  "MSL 4",  72,         30.0, 60.0 }, /* 3 доби */
    { MSL_LEVEL_5,  "MSL 5",  48,         30.0, 60.0 }, /* 2 доби */
    { MSL_LEVEL_5A, "MSL 5a", 24,         30.0, 60.0 }, /* 1 доба */
    { MSL_LEVEL_6,  "MSL 6",  6,          30.0, 60.0 }  /* Обов'язковий bake */
};

/* Розрахунок одиниць осушувача (Desiccant Units) за EIA-583 / J-STD-033 */
double calculate_desiccant_units(double bag_length_in, double bag_width_in,
                                 double wvtr_g_per_100sqin_day, double shelf_life_months) {
    double total_area_sqin = 2.0 * bag_length_in * bag_width_in;
    double d_cap = 0.16; /* Вологоємність однієї одиниці осушувача при 10% RH */
    return (0.011 * total_area_sqin * wvtr_g_per_100sqin_day * shelf_life_months) / d_cap;
}

/* Коефіцієнт дерайтингу Floor Life при зміні температури та вологості цеху */
double calculate_derating_factor(double ambient_temp_c, double ambient_rh_percent) {
    /* Розрахунок тиску насиченої пари за формулою Тетенса */
    double p_sat = 0.61078 * exp((17.27 * ambient_temp_c) / (ambient_temp_c + 237.3));
    double p_actual = (ambient_rh_percent / 100.0) * p_sat;
    
    /* Номінальний тиск пари при стандартних 30 °C / 60% RH */
    double p_sat_nominal = 0.61078 * exp((17.27 * 30.0) / (30.0 + 237.3));
    double p_nominal = 0.60 * p_sat_nominal;
    
    return p_actual / p_nominal;
}

/* Аналіз статусу відновлення Floor Life за стандартом J-STD-033 */
typedef struct {
    bool requires_baking;
    bool fully_recovered;
    double remaining_floor_life_hours;
    double required_dry_cabinet_hours;
    const char* action_message;
} msl_status_t;

msl_status_t evaluate_msl_exposure(msl_level_t level, double exposed_hours, 
                                   double time_in_dry_cab_hours, double dry_cab_rh,
                                   double ambient_temp_c, double ambient_rh_percent) {
    msl_status_t result = {0};
    const msl_spec_t* spec = &MSL_SPECS[level];

    if (spec->floor_life_hours == UINT32_MAX) {
        result.requires_baking = false;
        result.fully_recovered = true;
        result.remaining_floor_life_hours = (double)UINT32_MAX;
        result.action_message = "MSL 1: Необмежений строк цехового життя.";
        return result;
    }

    double derating = calculate_derating_factor(ambient_temp_c, ambient_rh_percent);
    double effective_exposed = exposed_hours * derating;
    double max_short_exp = (level <= MSL_LEVEL_3) ? 12.0 : 8.0;

    if (effective_exposed > spec->floor_life_hours) {
        result.requires_baking = true;
        result.fully_recovered = false;
        result.remaining_floor_life_hours = 0.0;
        result.action_message = "КРИТИЧНО: Floor Life вичерпано! Потрібне сушіння при 125 °C або 40 °C.";
        return result;
    }

    if (dry_cab_rh <= 5.0) {
        double needed_dry_time = 5.0 * exposed_hours;
        result.required_dry_cabinet_hours = needed_dry_time;
        if (exposed_hours <= max_short_exp && time_in_dry_cab_hours >= needed_dry_time) {
            result.fully_recovered = true;
            result.remaining_floor_life_hours = (double)spec->floor_life_hours;
            result.action_message = "Успіх: Floor Life повністю відновлено за правилом 5x.";
        } else {
            result.fully_recovered = false;
            result.remaining_floor_life_hours = (double)spec->floor_life_hours - effective_exposed;
            result.action_message = "У процесі сухого відновлення (RH < 5%).";
        }
    } else if (dry_cab_rh <= 10.0) {
        result.fully_recovered = false;
        result.remaining_floor_life_hours = (double)spec->floor_life_hours - effective_exposed;
        result.action_message = "Суха шафа RH < 10%: лічильник на паузі, але не відновлюється.";
    } else {
        result.remaining_floor_life_hours = (double)spec->floor_life_hours - (effective_exposed + time_in_dry_cab_hours);
        if (result.remaining_floor_life_hours <= 0.0) {
            result.requires_baking = true;
            result.remaining_floor_life_hours = 0.0;
            result.action_message = "УВАГА: Вологе сховище, строк вичерпано!";
        } else {
            result.action_message = "Увага: Вологість сховища > 10%, Floor Life продовжує втрачатися.";
        }
    }

    return result;
}
