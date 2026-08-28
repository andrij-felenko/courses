#include "driver/mcpwm.h"

static const int HS_PIN = 26;   // верхній ключ (high-side)
static const int LS_PIN = 27;   // нижній ключ (low-side)

// мертвий час у тактах 100 нс: скільки паузи вставити між вимкненням
// одного ключа й увімкненням іншого. Має ПЕРЕКРИВАТИ час перемикання!
static const uint32_t DEADTIME_NS = 300;   // 300 нс = 3× наш t_sw (100 нс) — із запасом

void halfbridge_init(void) {
    mcpwm_gpio_init(MCPWM_UNIT_0, MCPWM0A, HS_PIN);
    mcpwm_gpio_init(MCPWM_UNIT_0, MCPWM0B, LS_PIN);

    mcpwm_config_t cfg = {
        .frequency    = 20000,
        .cmpr_a       = 0.0f,                    // старт: обидва закриті
        .cmpr_b       = 0.0f,
        .duty_mode    = MCPWM_DUTY_MODE_0,
        .counter_mode = MCPWM_UP_COUNTER,
    };
    mcpwm_init(MCPWM_UNIT_0, MCPWM_TIMER_0, &cfg);

    // апаратний мертвий час: комплементарний режим, HS і LS ніколи не разом.
    // аргументи — у тактах по 100 нс, тому DEADTIME_NS/100.
    mcpwm_deadtime_enable(MCPWM_UNIT_0, MCPWM_TIMER_0,
                          MCPWM_ACTIVE_HIGH_COMPLEMENT_MODE,
                          DEADTIME_NS / 100, DEADTIME_NS / 100);
}

void halfbridge_set_duty(float pct) {
    if (pct < 2)  pct = 2;      // не даємо ключам «злипатися» на краях
    if (pct > 98) pct = 98;
    mcpwm_set_duty(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_OPR_A, pct);
    mcpwm_set_duty(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_OPR_B, 100.0f - pct);
}
