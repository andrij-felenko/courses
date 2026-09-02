#ifndef POWER_H
#define POWER_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    BATT_OK = 0,
    BATT_LOW,
    BATT_CRITICAL
} batt_level_t;

bool power_hold_on(void);
void power_release(void);
void power_sample_battery(void);
uint16_t power_battery_mv(void);
batt_level_t power_level(void);

#endif
