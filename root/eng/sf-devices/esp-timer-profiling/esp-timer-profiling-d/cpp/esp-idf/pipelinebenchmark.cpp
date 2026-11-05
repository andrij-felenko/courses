#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <cstdint>
#include "esp_cpu.h"
#include "esp_timer.h"
#include "esp_log.h"

namespace SystemProfiler {

class PipelineBenchmark {
public:
    static constexpr size_t kSampleCount = 100;
    static constexpr size_t kBufferSize = 256;

    struct Sample {
        uint32_t acquire_cycles;
        uint32_t filter_cycles;
        uint32_t transmit_cycles;
        uint32_t total_cycles;
    };

    void runBenchmark() {
        std::vector<Sample> samples;
        samples.reserve(kSampleCount);
        std::vector<uint8_t> buffer(kBufferSize, 0);

        for (size_t i = 0; i < kSampleCount; ++i) {
            uint32_t t0 = esp_cpu_get_cycle_count();
            acquireData(buffer);

            uint32_t t1 = esp_cpu_get_cycle_count();
            filterData(buffer);

            uint32_t t2 = esp_cpu_get_cycle_count();
            transmitData(buffer);

            uint32_t t3 = esp_cpu_get_cycle_count();

            samples.push_back({
                t1 - t0,
                t2 - t1,
                t3 - t2,
                t3 - t0
            });
        }

        analyzeResults(samples);
    }

private:
    void acquireData(std::vector<uint8_t>& buf) {
        for (size_t i = 0; i < buf.size(); ++i) {
            buf[i] = static_cast<uint8_t>(i & 0xFF);
        }
    }

    void filterData(std::vector<uint8_t>& buf) {
        // Вузьке місце конвеєра
        for (auto& byte : buf) {
            byte = (byte ^ 0xAA) + 1;
        }
    }

    void transmitData(const std::vector<uint8_t>& buf) {
        volatile uint32_t checksum = 0;
        for (const auto& byte : buf) {
            checksum += byte;
        }
        (void)checksum;
    }

    void analyzeResults(std::vector<Sample>& samples) {
        uint64_t sum_acquire = 0, sum_filter = 0, sum_transmit = 0;
        std::vector<uint32_t> totals;
        totals.reserve(samples.size());

        for (const auto& s : samples) {
            sum_acquire += s.acquire_cycles;
            sum_filter += s.filter_cycles;
            sum_transmit += s.transmit_cycles;
            totals.push_back(s.total_cycles);
        }

        std::sort(totals.begin(), totals.end());

        uint32_t p50 = totals[totals.size() / 2];
        uint32_t p99 = totals[(totals.size() * 99) / 100];
        uint32_t worst = totals.back();

        ESP_LOGI("CPP_PROFILER", "=== СТАТИСТИКА КОНВЕЄРА (C++) ===");
        ESP_LOGI("CPP_PROFILER", "Середній час Acquire:  %" PRIu64 " тактів", sum_acquire / kSampleCount);
        ESP_LOGI("CPP_PROFILER", "Середній час Filter:   %" PRIu64 " тактів [ВУЗЬКЕ МІСЦЕ]", sum_filter / kSampleCount);
        ESP_LOGI("CPP_PROFILER", "Середній час Transmit: %" PRIu64 " тактів", sum_transmit / kSampleCount);
        ESP_LOGI("CPP_PROFILER", "Перцентиль p50: %" PRIu32 " тактів", p50);
        ESP_LOGI("CPP_PROFILER", "Перцентиль p99: %" PRIu32 " тактів", p99);
        ESP_LOGI("CPP_PROFILER", "Максимальна затримка: %" PRIu32 " тактів", worst);
    }
};

} // namespace SystemProfiler

extern "C" void app_main(void)
{
    SystemProfiler::PipelineBenchmark benchmark;
    benchmark.runBenchmark();
}
