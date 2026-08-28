/* bsp_interface.h — Апаратний контракт плати (C) */
#ifndef BSP_INTERFACE_H
#define BSP_INTERFACE_H

#include <stdbool.h>
#include <stdint.h>

void bsp_system_init(void);
void bsp_led_heartbeat_toggle(void);
void bsp_debug_put_char(char ch);
bool bsp_is_power_good(void);

#endif
