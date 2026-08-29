/* supervisor.h — бізнес-логіка автономного реєстратора.
 * 100% переносний код: компілюється і під ARM, і під x86-64 хоста.
 */
#ifndef SUPERVISOR_H
#define SUPERVISOR_H

#include "bsp_interface.h"

/* Пороги й витримки — політика пристрою, а не властивість кремнію,
 * тому живуть тут, а не в драйвері плати. */
#define SUPERVISOR_VBAT_WARNING_MV   3300u
#define SUPERVISOR_VBAT_CRITICAL_MV  3000u
#define SUPERVISOR_SENSOR_SETTLE_MS    15u      /* заряд фільтрів після подачі живлення */
#define SUPERVISOR_ENV_ATTEMPTS         3u      /* стільки спроб на одне вимірювання */
#define SUPERVISOR_RETRY_PAUSE_MS       5u
#define SUPERVISOR_DEEP_SLEEP_MS  3600000u      /* 1 година */
#define SUPERVISOR_CYCLE_PERIOD_MS   60000u     /* опитування раз на хвилину */

typedef struct {
    const bsp_driver_t *bsp;        /* ПЕРШЕ поле: зміщення 0 для непрямого виклику */
    bool is_low_power_warning;
    bool is_critical_shutdown;
    bool has_fresh_env;             /* чи вдалося зчитати давачі в цьому циклі */
    board_env_metrics_t last_env;   /* останнє успішне вимірювання */
    uint32_t env_fault_count;       /* лічильник НЕВДАЛИХ спроб читання давачів */
    uint32_t battery_fault_count;
    uint32_t cycles;
} supervisor_t;

/* Прив'язує модуль до плати. Повертає BSP_STATUS_ERR_INVALID_PARAM,
 * якщо в таблиці бракує хоч одного методу. */
bsp_status_t supervisor_init(supervisor_t *ctx, const bsp_driver_t *bsp);

/* Один повний цикл нагляду. Ніколи не блокується назавжди:
 * кількість спроб читання давачів обмежена SUPERVISOR_ENV_ATTEMPTS. */
void supervisor_run_cycle(supervisor_t *ctx);

#endif /* SUPERVISOR_H */
