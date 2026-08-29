// bsp/bsp_power.h — ключ MOSFET, яким плата вимикає живлення лінії давачів.
// Знає про плату (полярність ключа, час розряду ємностей), але не про чип.
#ifndef BSP_POWER_H
#define BSP_POWER_H

#include "hal/hal_gpio.h"
#include "hal/hal_time.h"

typedef struct {
    hal_gpio_pin_t enable_pin;
    hal_time_t time;
    hal_gpio_level_t active_level;  // Рівень, яким ключ ВІДКРИТО (залежить від схеми)
    uint16_t off_hold_ms;           // Скільки тримати знеструмленим, щоб ємності розрядились
    uint16_t startup_ms;            // Скільки чекати після подання живлення
    uint32_t cycles;                // Лічильник перезапусків — потрапляє в діагностику
} bsp_power_t;

void bsp_power_init(bsp_power_t* p, hal_gpio_pin_t enable_pin, hal_time_t time,
                    hal_gpio_level_t active_level, uint16_t off_hold_ms, uint16_t startup_ms);

bool bsp_power_sensors_on(bsp_power_t* p);
bool bsp_power_sensors_off(bsp_power_t* p);

// Вимкнути, витримати, увімкнути, витримати старт. Саме цей виклик рятує шину,
// коли давач притиснув SDA до землі й не відпускає.
bool bsp_power_cycle_sensors(bsp_power_t* p);

#endif  // BSP_POWER_H
