#include <iostream>
#include <cstdint>
#include "esp_cpu.h"
#include "esp_timer.h"
#include "esp_clk_tree.h"
#include "esp_log.h"

static const char *TAG = "PROFILING_HARNESS";

#define COMPILER_BARRIER() asm volatile("" ::: "memory")

class PreciseProfiler {
public:
    static uint32_t getOverhead() {
        uint32_t start = esp_cpu_get_cycle_count();
        COMPILER_BARRIER();
        COMPILER_BARRIER();
        uint32_t end = esp_cpu_get_cycle_count();
        return (end - start);
    }
};

static void run_critical_algorithm()
{
    volatile double val = 1.0;
    for (int i = 0; i < 500; ++i) {
        val = val * 1.001 + 0.005;
    }
}

extern "C" void app_main(void)
{
    uint32_t overhead_cycles = PreciseProfiler::getOverhead();

    uint32_t cpu_freq_hz = 0;
    esp_clk_tree_src_get_freq_hz(SOC_MOD_CLK_CPU, ESP_CLK_TREE_SRC_FREQ_PRECISION_EXACT, &cpu_freq_hz);
    uint32_t cpu_freq_mhz = cpu_freq_hz / 1000000;

    COMPILER_BARRIER();
    uint32_t cycles_start = esp_cpu_get_cycle_count();
    COMPILER_BARRIER();

    run_critical_algorithm();

    COMPILER_BARRIER();
    uint32_t cycles_end = esp_cpu_get_cycle_count();
    COMPILER_BARRIER();

    uint32_t elapsed_cycles = (cycles_end >= cycles_start) ? 
                               (cycles_end - cycles_start) : 
                               (UINT32_MAX - cycles_start + cycles_end + 1);

    uint32_t net_cycles = (elapsed_cycles > overhead_cycles) ? (elapsed_cycles - overhead_cycles) : 0;
    double duration_us = static_cast<double>(net_cycles) / static_cast<double>(cpu_freq_mhz);

    ESP_LOGI(TAG, "Частота CPU: %u МГц", static_cast<unsigned int>(cpu_freq_mhz));
    ESP_LOGI(TAG, "Оверхед заміру: %u тактів", static_cast<unsigned int>(overhead_cycles));
    ESP_LOGI(TAG, "Тривалість виконання: %u тактів (чиста) = %.3f мкс", static_cast<unsigned int>(net_cycles), duration_us);
}
