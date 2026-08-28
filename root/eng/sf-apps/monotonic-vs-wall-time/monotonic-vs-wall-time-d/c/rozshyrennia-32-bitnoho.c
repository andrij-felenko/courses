#include <stdint.h>
#include <stdbool.h>

static volatile uint32_t s_high_epoch = 0;

void SysTick_Handler_64(void) {
    static uint32_t s_last_raw = 0;
    uint32_t current_raw = get_hardware_counter_32();
    if (current_raw < s_last_raw) {
        s_high_epoch++; // переповнення нижнього регістру
    }
    s_last_raw = current_raw;
}

uint64_t get_uptime_64(void) {
    uint32_t high1, high2, low;
    do {
        high1 = s_high_epoch;
        low   = get_hardware_counter_32();
        high2 = s_high_epoch;
    } while (high1 != high2); // повторити, якщо під час читання стався інкремент епохи
    
    return ((uint64_t)high1 << 32) | low;
}
