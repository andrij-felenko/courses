/* supervisor.c — рішення про живлення й вимірювання.
 * Жодного звернення до регістрів: усе через таблицю ctx->bsp.
 */
#include "supervisor.h"

#include <string.h>

/* Повторюємо читання давачів обмежену кількість разів.
 * Саме тут ловиться інжекція збою шини з тесту: без стелі спроб
 * один непрацездатний BME280 підвісив би весь пристрій. */
static bool read_env_retrying(supervisor_t *ctx, board_env_metrics_t *env)
{
    for (unsigned attempt = 0; attempt < SUPERVISOR_ENV_ATTEMPTS; ++attempt) {
        if (ctx->bsp->read_environment(env) == BSP_STATUS_OK) {
            env->timestamp_ms = ctx->bsp->uptime_ms();
            return true;
        }
        ctx->env_fault_count++;
        /* шина могла бути зайнята сусіднім майстром — даємо їй видихнути */
        ctx->bsp->delay_ms(SUPERVISOR_RETRY_PAUSE_MS);
    }
    return false;
}

bsp_status_t supervisor_init(supervisor_t *ctx, const bsp_driver_t *bsp)
{
    if (ctx == NULL || bsp == NULL) {
        return BSP_STATUS_ERR_INVALID_PARAM;
    }
    if (bsp->led_set == NULL || bsp->power_domain_set == NULL ||
        bsp->get_battery_metrics == NULL || bsp->read_environment == NULL ||
        bsp->enter_low_power == NULL || bsp->delay_ms == NULL ||
        bsp->uptime_ms == NULL) {
        return BSP_STATUS_ERR_INVALID_PARAM;
    }

    memset(ctx, 0, sizeof(*ctx));
    ctx->bsp = bsp;
    return BSP_STATUS_OK;
}

void supervisor_run_cycle(supervisor_t *ctx)
{
    if (ctx == NULL || ctx->bsp == NULL) {
        return;
    }

    ctx->cycles++;
    ctx->has_fresh_env = false;
    ctx->is_critical_shutdown = false;

    board_battery_metrics_t bat = {0};
    if (ctx->bsp->get_battery_metrics(&bat) != BSP_STATUS_OK) {
        /* Напруга невідома — поводимося обережно: сигналимо і чекаємо
         * наступного циклу. Знеструмлювати наосліп не можна: збій міг
         * бути в самому АЦП, а не в батареї. */
        ctx->battery_fault_count++;
        ctx->bsp->led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_ON);
        return;
    }

    /* Критичний поріг: гасимо все, що їсть струм, і лягаємо на годину. */
    if (bat.voltage_mv < SUPERVISOR_VBAT_CRITICAL_MV) {
        ctx->is_critical_shutdown = true;
        ctx->is_low_power_warning = true;
        ctx->bsp->led_set(BOARD_LED_ID_SYSTEM_STATUS, BOARD_LED_STATE_OFF);
        ctx->bsp->led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_ON);
        ctx->bsp->power_domain_set(BOARD_POWER_DOMAIN_RADIO, false);
        ctx->bsp->power_domain_set(BOARD_POWER_DOMAIN_SENSORS, false);
        ctx->bsp->enter_low_power(BOARD_SLEEP_MODE_DEEP, SUPERVISOR_DEEP_SLEEP_MS);
        return;
    }

    /* Попереджувальний поріг: вимірювати ще можна, а от передавати —
     * ні: імпульс струму радіомодуля просадить банку нижче критичної. */
    if (bat.voltage_mv < SUPERVISOR_VBAT_WARNING_MV) {
        ctx->is_low_power_warning = true;
        ctx->bsp->led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_ON);
        ctx->bsp->power_domain_set(BOARD_POWER_DOMAIN_RADIO, false);
    } else {
        ctx->is_low_power_warning = false;
        ctx->bsp->led_set(BOARD_LED_ID_WARNING, BOARD_LED_STATE_OFF);
        ctx->bsp->power_domain_set(BOARD_POWER_DOMAIN_RADIO, true);
    }

    /* Штатний цикл збору даних. */
    ctx->bsp->led_set(BOARD_LED_ID_SYSTEM_STATUS, BOARD_LED_STATE_ON);

    if (ctx->bsp->power_domain_set(BOARD_POWER_DOMAIN_SENSORS, true) == BSP_STATUS_OK) {
        /* Витримка стабілізації — інваріант, який перевіряє хостовий тест. */
        ctx->bsp->delay_ms(SUPERVISOR_SENSOR_SETTLE_MS);

        board_env_metrics_t env = {0};
        if (read_env_retrying(ctx, &env)) {
            ctx->last_env = env;
            ctx->has_fresh_env = true;
        }

        /* Знеструмлюємо давачі в БУДЬ-ЯКОМУ разі — навіть після трьох збоїв. */
        ctx->bsp->power_domain_set(BOARD_POWER_DOMAIN_SENSORS, false);
    }

    ctx->bsp->led_set(BOARD_LED_ID_SYSTEM_STATUS, BOARD_LED_STATE_OFF);
}
