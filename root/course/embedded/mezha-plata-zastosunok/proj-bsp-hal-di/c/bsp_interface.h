/* bsp_interface.h — контракт плати: типи й таблиця методів драйвера.
 *
 * Це єдиний заголовок, який бачить бізнес-логіка. Тут НЕМАЄ жодної згадки
 * про STM32, ESP32 чи будь-який інший кремній — лише поняття, якими
 * говорить плата: світлодіоди, домени живлення, батарея, середовище, сон.
 */
#ifndef BSP_INTERFACE_H
#define BSP_INTERFACE_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    BSP_STATUS_OK = 0,
    BSP_STATUS_ERR_INVALID_PARAM,
    BSP_STATUS_ERR_UNSUPPORTED,
    BSP_STATUS_ERR_TIMEOUT,
    BSP_STATUS_ERR_BUS_FAULT
} bsp_status_t;

typedef enum {
    BOARD_LED_ID_SYSTEM_STATUS = 0,
    BOARD_LED_ID_WARNING,
    BOARD_LED_ID_COUNT
} board_led_id_t;

typedef enum {
    BOARD_LED_STATE_OFF = 0,
    BOARD_LED_STATE_ON
} board_led_state_t;

typedef enum {
    BOARD_POWER_DOMAIN_SENSORS = 0,
    BOARD_POWER_DOMAIN_RADIO,
    BOARD_POWER_DOMAIN_COUNT
} board_power_domain_t;

typedef enum {
    BOARD_SLEEP_MODE_LIGHT = 0,  /* ядро спить, периферія жива */
    BOARD_SLEEP_MODE_DEEP        /* зупинка тактування, вихід за будильником */
} board_sleep_mode_t;

typedef struct {
    uint16_t voltage_mv;      /* напруга на клемах акумулятора, мВ */
    uint8_t  charge_percent;  /* груба оцінка заряду за напругою, 0..100 */
} board_battery_metrics_t;

typedef struct {
    int16_t  temperature_centi_c;  /* температура в сотих градуса Цельсія */
    uint32_t timestamp_ms;         /* мітка часу вимірювання (uptime плати) */
} board_env_metrics_t;

/* Таблиця методів драйвера плати.
 *
 * Порядок полів має значення для читання дизасемблера: led_set лежить
 * за нульовим зміщенням, тому виклик через покажчик згортається у
 * LDR r3,[r0,#0] / LDR r3,[r3,#0] / BLX r3.
 *
 * Усі методи ОБОВ'ЯЗКОВІ: supervisor_init перевіряє таблицю на повноту
 * й відмовляється працювати з дірками — краще впасти на старті, ніж
 * піймати HardFault за нульовим покажчиком через тиждень у полі.
 */
typedef struct {
    bsp_status_t (*led_set)(board_led_id_t led, board_led_state_t state);
    bsp_status_t (*power_domain_set)(board_power_domain_t domain, bool enable);
    bsp_status_t (*get_battery_metrics)(board_battery_metrics_t *metrics);
    bsp_status_t (*read_environment)(board_env_metrics_t *env);
    bsp_status_t (*enter_low_power)(board_sleep_mode_t mode, uint32_t timeout_ms);
    void         (*delay_ms)(uint32_t ms);
    uint32_t     (*uptime_ms)(void);
} bsp_driver_t;

#endif /* BSP_INTERFACE_H */
