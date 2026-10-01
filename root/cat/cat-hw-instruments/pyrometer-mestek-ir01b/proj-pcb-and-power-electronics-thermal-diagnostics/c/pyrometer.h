#ifndef PYROMETER_H
#define PYROMETER_H

#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Фізичні константи */
#define STEFAN_BOLTZMAN_SIGMA 5.670374e-8f  /* Вт/(м²·К⁴) */
#define ABSOLUTE_ZERO_CELSIUS -273.15f      /* Зсув температури Кельвіна */

/* Паспортні межі вимірювання MESTEK IR01B */
#define PYRO_MIN_TEMP_CELSIUS -50.0f
#define PYRO_MAX_TEMP_CELSIUS 550.0f
#define PYRO_MIN_EMISSIVITY   0.10f
#define PYRO_MAX_EMISSIVITY   1.00f

/* Коди статусу та помилок */
typedef enum {
    PYRO_OK = 0,
    PYRO_WARN_HIGH_ALARM,
    PYRO_WARN_LOW_ALARM,
    PYRO_ERR_INVALID_EMISSIVITY,
    PYRO_ERR_OUT_OF_RANGE_LOW,
    PYRO_ERR_OUT_OF_RANGE_HIGH,
    PYRO_ERR_SENSOR_FAULT
} pyro_status_t;

/* Структура конфігурації пірометра */
typedef struct {
    float emissivity;         /* Коефіцієнт емісії ε (0.10 ... 1.00) */
    float bg_temp_celsius;    /* Фонова температура навколишнього середовища T_bg (°C) */
    float k_sensor;           /* Чутливість термостовпчика (В/К⁴) */
    float high_alarm_celsius; /* Верхня межа тривоги HAL (°C) */
    float low_alarm_celsius;  /* Нижня межа тривоги LAL (°C) */
    float hysteresis_celsius; /* Гістерезис для запобігання брязкіту тривоги (°C) */
} pyro_config_t;

/* Структура результату вимірювання */
typedef struct {
    float object_temp_celsius; /* Розрахована дійсна температура об'єкта (°C) */
    float raw_voltage_mv;      /* Виміряна напруга термостовпчика (мВ) */
    float ambient_temp_celsius;/* Температура датчика / холодного спаю (°C) */
    pyro_status_t status;      /* Поточний статус вимірювання */
    bool high_alarm_active;    /* Прапорець активності верхньої тривоги HAL */
    bool low_alarm_active;     /* Прапорець активності нижньої тривоги LAL */
} pyro_reading_t;

/* Функції ініціалізації та обчислення */
pyro_status_t pyro_init_config(pyro_config_t *config);

pyro_status_t pyro_calculate_temperature(
    const pyro_config_t *config,
    float raw_voltage_v,
    float ambient_temp_celsius,
    pyro_reading_t *reading
);

pyro_status_t pyro_update_alarms(
    const pyro_config_t *config,
    pyro_reading_t *reading
);

float pyro_celsius_to_kelvin(float celsius);
float pyro_kelvin_to_celsius(float kelvin);

#ifdef __cplusplus
}
#endif

#endif /* PYROMETER_H */
