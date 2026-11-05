#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include "esp_cpu.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

class IsolatedProfiler {
public:
    template<typename Func>
    static void run_analysis(size_t runs, Func&& bench_func) {
        std::vector<uint32_t> samples;
        samples.reserve(runs);

        portMUX_TYPE spinlock = portMUX_INITIALIZER_UNLOCKED;

        // Warm-up кєшу інструкцій
        bench_func();

        for (size_t r = 0; r < runs; ++r) {
            taskENTER_CRITICAL(&spinlock);
            
            asm volatile("" ::: "memory");
            uint32_t start = esp_cpu_get_cycle_count();
            
            bench_func();
            
            asm volatile("" ::: "memory");
            uint32_t end = esp_cpu_get_cycle_count();
            
            taskEXIT_CRITICAL(&spinlock);

            samples.push_back(end - start);
        }

        std::sort(samples.begin(), samples.end());

        uint32_t min_val = samples.front();
        uint32_t max_val = samples.back();
        uint32_t median_val = samples[samples.size() / 2];
        uint32_t p95_val = samples[static_cast<size_t>(samples.size() * 0.95)];

        std::cout << "Statistical Profile (" << runs << " runs):\n"
                  << "  Min (Pure Hardware Limit): " << min_val << " cycles\n"
                  << "  Median:                    " << median_val << " cycles\n"
                  << "  P95 Latency:               " << p95_val << " cycles\n"
                  << "  Max Spike:                 " << max_val << " cycles\n";
    }
};
