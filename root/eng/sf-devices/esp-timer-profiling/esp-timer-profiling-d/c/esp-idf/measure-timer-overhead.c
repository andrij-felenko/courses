#include <stdio.h>
#include <stdint.h>
#include "esp_cpu.h"
#include "esp_clk.h"

#define CALIBRATION_LOOPS 1000

// Функція обчислення систематичного оверхеду зчитування CCOUNT
static uint32_t measure_timer_overhead(void) {
    uint32_t min_overhead = UINT32_MAX;
    
    for (int i = 0; i < CALIBRATION_LOOPS; i++) {
        uint32_t start = esp_cpu_get_cycle_count();
        // Порожній блок коду з бар'єром пам'яті
        __asm__ __volatile__("" ::: "memory");
        uint32_t end = esp_cpu_get_cycle_count();
        
        uint32_t delta = end - start; // Беззнакова арифметика за модулем 2^32
        if (delta < min_overhead) {
            min_overhead = delta;
        }
    }
    return min_overhead;
}

// Приклад вимірювання функції з відніманням оверхеду
void profile_target_function(void) {
    uint32_t overhead = measure_timer_overhead();
    uint32_t cpu_freq_mhz = esp_clk_cpu_freq() / 1000000;
    
    uint32_t start = esp_cpu_get_cycle_count();
    
    // Код, що підлягає вимірюванню
    volatile double val = 1.0;
    for (int i = 0; i < 50; i++) {
        val *= 1.001;
    }
    __asm__ __volatile__("" ::: "memory");
    
    uint32_t end = esp_cpu_get_cycle_count();
    
    uint32_t raw_cycles = end - start;
    uint32_t net_cycles = (raw_cycles > overhead) ? (raw_cycles - overhead) : 0;
    uint32_t time_ns = (net_cycles * 1000) / cpu_freq_mhz;
    
    printf("Raw: %lu cycles, Overhead: %lu cycles, Net: %lu cycles (%lu ns)\n",
           (unsigned long)raw_cycles, (unsigned long)overhead,
           (unsigned long)net_cycles, (unsigned long)time_ns);
}
