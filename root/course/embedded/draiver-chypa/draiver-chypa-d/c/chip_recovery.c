#include <stddef.h>

#include "chip_recovery.h"

/* Півперіоду такту ~5 мкс ≈ 100 кГц: повільно, зате переживає будь-яку
 * ємність шини й будь-який сонний ведений. */
#define RECOVERY_HALF_PERIOD_US 5u
#define RECOVERY_CLOCK_PULSES   9u

chip_status_t chip_bus_recover(const chip_gpio_ops_t *gpio, void *user_ctx)
{
    if (gpio == NULL || gpio->scl_set == NULL || gpio->sda_set == NULL ||
        gpio->sda_get == NULL || gpio->delay_us == NULL) {
        return CHIP_ERR_INVALID_PARAM;
    }

    /* Крок 1: відпускаємо обидві лінії — тепер їх тримає лише той, хто завис. */
    gpio->sda_set(user_ctx, true);
    gpio->scl_set(user_ctx, true);
    gpio->delay_us(RECOVERY_HALF_PERIOD_US);

    bool released = gpio->sda_get(user_ctx);

    /* Крок 2: до дев'яти тактів SCL — рівно стільки бітів може лишатися в
     * зсувному регістрі веденого разом із тактом підтвердження. */
    for (unsigned pulse = 0; pulse < RECOVERY_CLOCK_PULSES && !released; ++pulse) {
        gpio->scl_set(user_ctx, false);
        gpio->delay_us(RECOVERY_HALF_PERIOD_US);
        gpio->scl_set(user_ctx, true);
        gpio->delay_us(RECOVERY_HALF_PERIOD_US);
        released = gpio->sda_get(user_ctx);
    }

    if (!released) {
        /* Лінія й далі в нулі: тактування не допомогло. */
        if (gpio->release != NULL) {
            gpio->release(user_ctx);
        }
        return CHIP_ERR_COMM;
    }

    /* Крок 3: умова STOP — SDA 0→1 при високому SCL. Після неї всі чипи на
     * шині повертаються в стан очікування START. */
    gpio->sda_set(user_ctx, false);
    gpio->delay_us(RECOVERY_HALF_PERIOD_US);
    gpio->scl_set(user_ctx, true);
    gpio->delay_us(RECOVERY_HALF_PERIOD_US);
    gpio->sda_set(user_ctx, true);
    gpio->delay_us(RECOVERY_HALF_PERIOD_US);

    if (gpio->release != NULL) {
        gpio->release(user_ctx);
    }
    return CHIP_OK;
}
