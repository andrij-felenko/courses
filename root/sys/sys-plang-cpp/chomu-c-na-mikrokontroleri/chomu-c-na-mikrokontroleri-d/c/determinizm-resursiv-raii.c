/* Критична секція мовою C із ризиком витоку блокування */
#include <stdint.h>
#include <stdbool.h>

/* Асемблерні макроси Cortex-M */
static inline uint32_t disable_interrupts(void) {
    uint32_t primask;
    __asm volatile ("mrs %0, primask\ncpsid i" : "=r"(primask) :: "memory");
    return primask;
}

static inline void restore_interrupts(uint32_t primask) {
    __asm volatile ("msr primask, %0" :: "r"(primask) : "memory");
}

bool process_sensor_c(int sensor_id, uint32_t* out_val) {
    uint32_t state = disable_interrupts();
    
    if (sensor_id < 0) {
        /* ДЕФЕКТ: Забули відновити переривання перед виходом! */
        return false; 
    }
    
    *out_val = *(volatile uint32_t*)0x40001000;
    restore_interrupts(state);
    return true;
}
