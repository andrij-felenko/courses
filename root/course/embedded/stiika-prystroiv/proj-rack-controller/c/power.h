/* Дві лінії керування слотом: силовий ключ VCC і ключ BOOT0. */
#ifndef RACK_POWER_H
#define RACK_POWER_H

#include "rack.h"

typedef struct {
    int lines_fd; /* дескриптор запиту ліній, виданий GPIO_V2_GET_LINE_IOCTL */
} rack_power_t;

void rack_power_init(rack_power_t *pwr);
rack_status_t rack_power_open(rack_power_t *pwr, int slot_id);
rack_status_t rack_power_vcc(rack_power_t *pwr, bool on);
rack_status_t rack_power_boot0(rack_power_t *pwr, bool high);
void rack_power_close(rack_power_t *pwr);

#endif /* RACK_POWER_H */
