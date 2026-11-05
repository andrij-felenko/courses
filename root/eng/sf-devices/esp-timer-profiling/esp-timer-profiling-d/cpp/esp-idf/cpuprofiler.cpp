#include <iostream>
#include <cstdint>
#include <algorithm>
#include "esp_cpu.h"
#include "esp_clk.h"

class CpuProfiler {
public:
    static uint32_t get_overhead(size_t iterations = 1000) {
        uint32_t min_overhead = UINT32_MAX;
        for (size_t i = 0; i < iterations; ++i) {
            uint32_t start = esp_cpu_get_cycle_count();
            asm volatile("" ::: "memory");
            uint32_t end = esp_cpu_get_cycle_count();
            
            uint32_t delta = end - start;
            if (delta < min_overhead) {
                min_overhead = delta;
            }
        }
        return min_overhead;
    }

    template<typename Func>
    static void profile(const char* name, Func&& func) {
        uint32_t overhead = get_overhead();
        uint32_t cpu_freq_mhz = esp_clk_cpu_freq() / 1000000;

        uint32_t start = esp_cpu_get_cycle_count();
        func();
        asm volatile("" ::: "memory");
        uint32_t end = esp_cpu_get_cycle_count();

        uint32_t raw_cycles = end - start;
        uint32_t net_cycles = (raw_cycles > overhead) ? (raw_cycles - overhead) : 0;
        uint32_t time_ns = (net_cycles * 1000) / cpu_freq_mhz;

        std::cout << "[" << name << "] Net cycles: " << net_cycles 
                  << " (" << time_ns << " ns), Overhead: " << overhead << " cycles\n";
    }
};
