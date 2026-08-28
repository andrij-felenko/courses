/* i2c_driver.c - Приватний файл реалізації C99 */
#include "i2c_driver.h"

struct i2c_driver_context_s {
    uintptr_t hw_base;
    uint32_t clock_hz;
    uint16_t timeout;
    volatile uint32_t state;
    volatile size_t bytes_transferred;
    /* Будь-які внутрішні змінні невидимі ззовні */
};

static struct i2c_driver_context_s s_instances[2]; /* Фіксований статичний пул */

i2c_handle_t i2c_create_instance(uint8_t port_index, const i2c_user_config_t* config) {
    if (port_index >= 2 || config == NULL) return NULL;
    struct i2c_driver_context_s* inst = &s_instances[port_index];
    inst->hw_base = (port_index == 0) ? 0x40005400 : 0x40005800;
    inst->clock_hz = config->clock_speed_hz;
    inst->timeout = config->timeout_ms;
    inst->state = 0;
    return inst;
}
