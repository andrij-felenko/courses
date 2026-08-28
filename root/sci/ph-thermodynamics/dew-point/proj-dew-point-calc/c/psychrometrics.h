/* psychrometrics.h — C99 бібліотека обчислення точки роси */
#ifndef PSYCHROMETRICS_H
#define PSYCHROMETRICS_H

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    PSYCHRO_OK = 0,
    PSYCHRO_ERR_TEMP_OUT_OF_RANGE = -1,
    PSYCHRO_ERR_HUMIDITY_OUT_OF_RANGE = -2,
    PSYCHRO_ERR_NULL_POINTER = -3
} psychro_error_t;

typedef struct {
    double air_temp_c;      /* Температура повітря, °C */
    double rel_humidity_pct;/* Відносна вологість, % */
    double dew_point_c;     /* Обчислена температура точки роси, °C */
    double frost_point_c;   /* Обчислена температура точки інею, °C */
    double sat_vapor_press_kpa; /* Тиск насиченої пари, кПа */
    double vapor_press_kpa;     /* Поточний парціальний тиск, кПа */
} psychro_result_t;

typedef struct {
    double temp_margin_on_c;  /* Поріг увімкнення нагрівача (напр. 2.0 °C) */
    double temp_margin_off_c; /* Поріг вимкнення нагрівача (напр. 4.0 °C) */
    bool heater_active;       /* Поточний стан нагрівача */
} anti_cond_controller_t;

/* Обчислення психометричних параметрів */
psychro_error_t psychro_calculate(double temp_c, double rh_pct, psychro_result_t *res);

/* Оновлення стану контролера запобігання конденсації */
bool anti_cond_update(anti_cond_controller_t *ctrl, double surface_temp_c, double dew_point_c);

#ifdef __cplusplus
}
#endif

#endif /* PSYCHROMETRICS_H */
