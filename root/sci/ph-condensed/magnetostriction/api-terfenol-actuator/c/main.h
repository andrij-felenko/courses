#ifndef GMM_ACTUATOR_H
#define GMM_ACTUATOR_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок API */
typedef enum {
    GMM_SUCCESS = 0,
    GMM_ERR_INVALID_PARAM = -1,
    GMM_ERR_NOT_CONNECTED = -2,
    GMM_ERR_OVERTEMPERATURE = -3,
    GMM_ERR_OVERCURRENT = -4,
    GMM_ERR_LVDT_FAILURE = -5,
    GMM_ERR_TIMEOUT = -6
} gmm_error_t;

/* Структура конфігурації приводу */
typedef struct {
    uint32_t can_node_id;       /* ID вузла CANopen (1..127) */
    uint32_t position_limit_nm; /* Максимальне дозволене зміщення (нм) */
    uint16_t max_current_ma;    /* Граничний струм котушки (мА) */
    uint16_t temp_limit_ddeg;   /* Поріг відключення по температурі (0.1 °C) */
} gmm_config_t;

/* Структура поточного телеметричного стану */
typedef struct {
    int32_t  actual_position_nm; /* Фактичне зміщення (нм) */
    int16_t  coil_current_ma;    /* Виміряний струм (мА) */
    int16_t  temperature_ddeg;   /* Температура стрижня (0.1 °C) */
    uint32_t status_flags;       /* Біти DriveStatus */
    bool     is_enabled;         /* Статус підсилювача */
} gmm_telemetry_t;

/* Дескриптор приводу */
typedef struct gmm_handle_struct* gmm_handle_t;

/* Ініціалізація та відкриття з'єднання з контролером */
gmm_error_t gmm_init(gmm_handle_t* handle, const gmm_config_t* config);

/* Закриття з'єднання та безпечне вимкнення приводу */
gmm_error_t gmm_close(gmm_handle_t handle);

/* Увімкнення/вимкнення силового підсилювача */
gmm_error_t gmm_enable(gmm_handle_t handle, bool enable);

/* Задання цільового зміщення у серво-режимі замкненого контуру (в нанометрах) */
gmm_error_t gmm_set_position(gmm_handle_t handle, int32_t position_nm);

/* Задання прямого струму котушки у відкритому контурі (в міліамперах) */
gmm_error_t gmm_set_current_open_loop(gmm_handle_t handle, int16_t current_ma);

/* Читання повної телеметрії приводу */
gmm_error_t gmm_get_telemetry(gmm_handle_t handle, gmm_telemetry_t* telemetry);

/* Скинути аварійний стан (Reset Fault) після усунення причини спрацювання */
gmm_error_t gmm_fault_reset(gmm_handle_t handle);

#ifdef __cplusplus
}
#endif

#endif /* GMM_ACTUATOR_H */
