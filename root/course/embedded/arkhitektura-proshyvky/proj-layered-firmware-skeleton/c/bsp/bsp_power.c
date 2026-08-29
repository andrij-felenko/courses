// bsp/bsp_power.c
#include "bsp/bsp_power.h"

#include <stddef.h>

static hal_gpio_level_t inactive_level(const bsp_power_t* p)
{
    return (p->active_level == HAL_GPIO_HIGH) ? HAL_GPIO_LOW : HAL_GPIO_HIGH;
}

void bsp_power_init(bsp_power_t* p, hal_gpio_pin_t enable_pin, hal_time_t time,
                    hal_gpio_level_t active_level, uint16_t off_hold_ms, uint16_t startup_ms)
{
    if (!p) return;
    p->enable_pin = enable_pin;
    p->time = time;
    p->active_level = active_level;
    p->off_hold_ms = off_hold_ms;
    p->startup_ms = startup_ms;
    p->cycles = 0u;
}

bool bsp_power_sensors_on(bsp_power_t* p)
{
    if (!p) return false;
    return hal_gpio_write(&p->enable_pin, p->active_level) == HAL_GPIO_OK;
}

bool bsp_power_sensors_off(bsp_power_t* p)
{
    if (!p) return false;
    return hal_gpio_write(&p->enable_pin, inactive_level(p)) == HAL_GPIO_OK;
}

bool bsp_power_cycle_sensors(bsp_power_t* p)
{
    if (!p) return false;

    if (!bsp_power_sensors_off(p)) return false;
    // Без витримки ємності на платі не встигають розрядитись, і давач
    // «переживає» скидання, лишаючись у тому самому завислому стані.
    hal_time_delay_ms(&p->time, p->off_hold_ms);

    if (!bsp_power_sensors_on(p)) return false;
    hal_time_delay_ms(&p->time, p->startup_ms);

    p->cycles++;
    return true;
}
