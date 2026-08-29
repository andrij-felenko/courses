#include "hw.h"
#include "safe_actuator.h"

/* Період головного циклу. Мусить бути коротшим за півперіод меандру,
 * інакше серцебиття втратить фронти ще до будь-якої аварії. */
#define CYCLE_PERIOD_US 250U

/* Профіль місії: розгін до 40% за секунду, утримання, зупинка. */
#define MISSION_RAMP_US  1000000U
#define MISSION_HOLD_US  5000000U
#define MISSION_TARGET   400U

static uint16_t mission_target_pwm(uint32_t armed_for_us)
{
    if (armed_for_us >= (MISSION_RAMP_US + MISSION_HOLD_US)) {
        return 0;
    }
    if (armed_for_us >= MISSION_RAMP_US) {
        return MISSION_TARGET;
    }
    /* Лінійний розгін. Множення робимо в 64 бітах: 400 * 1e6 не влазить
     * у 32 біти, і мовчазне переповнення дало б ривок на старті. */
    return (uint16_t)(((uint64_t)MISSION_TARGET * armed_for_us) /
                      MISSION_RAMP_US);
}

int main(void)
{
    safe_actuator_t drv;
    uint32_t armed_since_us = 0;
    bool mission_started = false;
    bool mission_done = false;

    /* Сторож стартує ПЕРШИМ: якщо зависне сама ініціалізація периферії,
     * контролер має вийти з цього сам. */
    hw_watchdog_start(WATCHDOG_TIMEOUT_MS);
    safe_actuator_init(&drv);

    if (!safe_actuator_request_arm(&drv, SAFE_ARM_TOKEN)) {
        /* Запит відхилено — драйвер уже в FAULT і виходи вже мертві.
         * Лишається крутити цикл, щоб годувати сторожа й тримати нуль. */
        for (;;) {
            safe_actuator_process_cycle(&drv, 0);
        }
    }

    for (;;) {
        const uint32_t cycle_start_us = hw_get_time_us();
        uint16_t target = 0;

        switch (safe_actuator_state(&drv)) {
        case ACTUATOR_ARMED:
            if (!mission_started) {
                mission_started = true;
                armed_since_us = cycle_start_us;
            }
            if (!mission_done) {
                const uint32_t armed_for = cycle_start_us - armed_since_us;
                target = mission_target_pwm(armed_for);
                if (armed_for >= (MISSION_RAMP_US + MISSION_HOLD_US)) {
                    mission_done = true;
                }
            }
            break;

        default:
            /* DISARMED, ARM_REQUESTED і PRE_ARM_CHECK проходять самі,
             * FAULT тримається до перезапуску. Ціль скрізь нульова. */
            break;
        }

        safe_actuator_process_cycle(&drv, target);

        if (mission_done && safe_actuator_state(&drv) == ACTUATOR_ARMED) {
            safe_actuator_disarm(&drv);
        }

        /* Витримка періоду. Активне очікування тут чесніше за сон: цикл
         * безпеки не має права заснути глибше, ніж дозволяє сторож. */
        while ((hw_get_time_us() - cycle_start_us) < CYCLE_PERIOD_US) {
            /* чекаємо наступного такту */
        }
    }
}
