/* eom_driver.h - C API специфікація контролера електрооптичного модулятора */
#ifndef EOM_DRIVER_H
#define EOM_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Типи електрооптичних кристалів */
typedef enum {
    EOM_CRYSTAL_DKDP = 0,
    EOM_CRYSTAL_LINBO3,
    EOM_CRYSTAL_BBO,
    EOM_CRYSTAL_KTP,
    EOM_CRYSTAL_CUSTOM
} eom_crystal_type_t;

/* Геометрія комірки Поккельса */
typedef enum {
    EOM_GEOMETRY_LONGITUDINAL = 0, /* E ∥ k */
    EOM_GEOMETRY_TRANSVERSE        /* E ⊥ k */
} eom_geometry_mode_t;

/* Режими стабілізації робочої точки (DC Bias Control) */
typedef enum {
    EOM_BIAS_MANUAL = 0,      /* Ручне встановлення напруги зсуву */
    EOM_BIAS_QUAD_NULL,       /* Автоматична підстройка під точка Quad (V_pi / 2) */
    EOM_BIAS_MIN_TRANSMISSION,/* Мінімум пропускання (для Q-switch / згасання) */
    EOM_BIAS_MAX_TRANSMISSION /* Максимум пропускання */
} eom_bias_mode_t;

/* Коди помилок драйвера */
typedef enum {
    EOM_SUCCESS = 0,
    EOM_ERROR_INVALID_PARAM = -1,
    EOM_ERROR_HV_OVERVOLTAGE = -2,
    EOM_ERROR_OVERTEMPERATURE = -3,
    EOM_ERROR_BIAS_LOCK_LOST = -4,
    EOM_ERROR_COMMUNICATION  = -5
} eom_status_code_t;

/* Конфігураційна структура модулятора */
typedef struct {
    eom_crystal_type_t crystal_type;
    eom_geometry_mode_t geometry;
    double wavelength_nm;         /* Довжина хвилі світла (нм) */
    double v_pi_nominal_volts;    /* Паспортна напівхвильова напруга (В) */
    double max_hv_volts;          /* Максимально припустима напруга (В) */
    double max_temperature_c;     /* Поріг теплового захисту (°C) */
} eom_config_t;

/* Стан та телеметрія контролера */
typedef struct {
    double current_bias_volts;    /* Поточна напруга зсуву (В) */
    double crystal_temp_c;        /* Температура кристала (°C) */
    double optical_power_mw;      /* Потужність на виході модулятора (мВт) */
    double thd_percent;           /* Коефіцієнт нелінійних спотворень (%) */
    bool hv_enabled;              /* Стан високовольтного блоку */
    bool bias_locked;             /* Стан захоплення робочої точки */
} eom_telemetry_t;

/* Дескриптор пристрою */
typedef struct eom_device* eom_handle_t;

/* --- Прототипи функцій API --- */

/* Ініціалізація та закриття драйвера */
eom_status_code_t eom_init(eom_handle_t* handle, uint8_t bus_id, uint8_t dev_addr);
eom_status_code_t eom_destroy(eom_handle_t handle);

/* Конфігурування параметрів */
eom_status_code_t eom_set_config(eom_handle_t handle, const eom_config_t* config);
eom_status_code_t eom_get_config(eom_handle_t handle, eom_config_t* config);

/* Керування високою напругою та зсувом */
eom_status_code_t eom_enable_hv(eom_handle_t handle, bool enable);
eom_status_code_t eom_set_manual_bias(eom_handle_t handle, double bias_volts);
eom_status_code_t eom_set_bias_mode(eom_handle_t handle, eom_bias_mode_t mode);

/* Калібрування та автоналаштування */
eom_status_code_t eom_calibrate_v_pi(eom_handle_t handle, double* measured_v_pi);
eom_status_code_t eom_scan_transmission_curve(eom_handle_t handle, double* buffer_v, double* buffer_power, uint16_t points);

/* Читання стану та телеметрії */
eom_status_code_t eom_get_telemetry(eom_handle_t handle, eom_telemetry_t* telemetry);

#ifdef __cplusplus
}
#endif

#endif /* EOM_DRIVER_H */
