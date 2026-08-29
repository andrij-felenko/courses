#ifndef BSP_TYPES_H
#define BSP_TYPES_H

#include "bsp/status.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Логічні ідентифікатори індикаторів плати.
 *
 * Застосунок оперує РОЛЛЮ світлодіода, а не номером виводу: полярність,
 * режим виходу й фізичний пін живуть у таблиці топології всередині BSP.
 */
typedef enum {
    BOARD_LED_ID_SYSTEM_STATUS = 0, /**< Системний світлодіод стану (Heartbeat) */
    BOARD_LED_ID_WARNING       = 1, /**< Індикатор попередження / аварії */
    BOARD_LED_ID_COMMS         = 2, /**< Індикатор активності бездротового зв'язку */
    BOARD_LED_ID_MAX
} board_led_id_t;

/**
 * @brief Логічний стан індикатора.
 */
typedef enum {
    BOARD_LED_STATE_OFF = 0,
    BOARD_LED_STATE_ON  = 1
} board_led_state_t;

/**
 * @brief Керовані домени живлення плати.
 */
typedef enum {
    BOARD_POWER_DOMAIN_SENSORS  = 0, /**< Лінія живлення зовнішніх давачів (I2C/SPI) */
    BOARD_POWER_DOMAIN_RADIO    = 1, /**< Модуль радіозв'язку (LoRa/BLE) */
    BOARD_POWER_DOMAIN_DISPLAY  = 2, /**< РК/OLED дисплей та його підсвітка */
    BOARD_POWER_DOMAIN_MAX
} board_power_domain_t;

/**
 * @brief Режими енергозбереження мікроконтролера.
 */
typedef enum {
    BOARD_SLEEP_MODE_LIGHT = 0, /**< Сон зі швидким пробудженням від таймера */
    BOARD_SLEEP_MODE_DEEP  = 1  /**< Глибокий сон з мінімальним струмом споживання */
} board_sleep_mode_t;

/**
 * @brief Метрики стану акумуляторної батареї.
 */
typedef struct {
    uint16_t voltage_mv;       /**< Напруга батареї в мілівольтах (наприклад, 3850 мВ) */
    uint8_t  charge_percent;   /**< Розрахований залишковий заряд у відсотках (0..100) */
    bool     is_charging;      /**< Прапорець підключення зовнішнього зарядного пристрою */
    bool     is_critical_low;  /**< Прапорець падіння напруги нижче безпечного порогу */
} board_battery_metrics_t;

/**
 * @brief Метрики навколишнього середовища.
 *
 * Фіксована кома замість float: молодші ядра не мають FPU, а цілі числа
 * пакуються в бінарний кадр без платформозалежної серіалізації.
 */
typedef struct {
    int16_t  temperature_centi_c; /**< Температура в сотих частках °C (2450 = 24.50 °C) */
    uint32_t pressure_pa;         /**< Атмосферний тиск у паскалях (101325 Па) */
    uint16_t humidity_centi_pct;  /**< Відносна вологість у сотих частках % (6540 = 65.40%) */
} board_env_metrics_t;

#ifdef __cplusplus
}
#endif

#endif /* BSP_TYPES_H */
