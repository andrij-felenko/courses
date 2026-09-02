/* Модель шини замість заліза: реалізує контракт з i2c_lines.h,
   щоб той самий код сканера можна було прогнати на робочій машині
   й побачити всі три типові діагнози. */
#ifndef SIM_LINES_H
#define SIM_LINES_H

#include <stdint.h>

typedef enum {
    SIM_FAULT_NONE,          /* справна шина з одним сенсором */
    SIM_FAULT_SDA_STUCK_LOW, /* ведений завис посеред байта й тримає SDA */
    SIM_FAULT_NO_PULLUPS,    /* підтяжок немає: лінії нікуди не піднімаються */
    SIM_FAULT_NO_POWER       /* лінії чисті, але сенсор не заживлений */
} sim_fault_t;

void sim_bus_init(uint8_t slave_addr7, sim_fault_t fault);

#endif /* SIM_LINES_H */
