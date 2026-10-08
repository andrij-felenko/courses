/* Оголошення типів та структур C API для Pt100/Pt1000 */
#ifndef RTD_API_H
#define RTD_API_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    RTD_TYPE_PT100  = 100,
    RTD_TYPE_PT1000 = 1000
} rtd_type_t;

typedef enum {
    RTD_CLASS_AA = 0,
    RTD_CLASS_A,
    RTD_CLASS_B,
    RTD_CLASS_C,
    RTD_CLASS_CUSTOM
} rtd_class_t;

typedef enum {
    RTD_OK = 0,
    RTD_ERR_OPEN_CIRCUIT,
    RTD_ERR_SHORT_CIRCUIT,
    RTD_ERR_OUT_OF_RANGE,
    RTD_ERR_SELF_HEATING,
    RTD_ERR_INVALID_PARAM
} rtd_status_t;

typedef struct {
    double A;
    double B;
    double C;
} rtd_cvd_coeff_t;

typedef struct {
    rtd_type_t     type;
    rtd_class_t    accuracy_class;
    double         r0;            /* Номінальний опір при 0 °C (Ом) */
    rtd_cvd_coeff_t coeff;         /* Коефіцієнти Каллендара — Ван Дюзена */
    double         r_min;         /* Поріг короткого замикання (Ом) */
    double         r_max;         /* Поріг обриву лінії (Ом) */
    double         max_current_a; /* Максимальний струм вимірювання (А) */
} rtd_config_t;

/* Функції ініціалізації конфігурації */
rtd_status_t rtd_config_init(rtd_config_t *config, rtd_type_t type, rtd_class_t accuracy_class);

#endif /* RTD_API_H */
