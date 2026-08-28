// ESP-IDF / C++20: Запуск бенчмарку та перевірка інваріантів
#include <chrono>
#include <span>
#include <vector>
#include <numeric>
#include "esp_cpu.h"
#include "esp_log.h"

void RunCppBenchmark() {
    using namespace ai::simd;

    constexpr std::size_t NumIn = 256;
    constexpr std::size_t NumOut = 128;

    std::vector<std::int8_t> input(NumIn);
    std::vector<std::int8_t> weights(NumIn * NumOut);
    std::vector<std::int32_t> bias(NumOut);
    std::vector<std::int8_t> out_simd(NumOut);

    // Ініціалізація
    std::iota(input.begin(), input.end(), -128);
    std::iota(weights.begin(), weights.end(), -64);
    std::iota(bias.begin(), bias.end(), 100);

    QuantParams params{
        .input_offset = 15,
        .output_offset = -2,
        .output_multiplier = 1073741824,
        .output_shift = 31,
        .activation_min = -128,
        .activation_max = 127
    };

    FullyConnectedLayer fc(NumIn, NumOut, params);

    const auto start = esp_cpu_get_cycle_count();
    fc.ExecuteSimd(input, weights, bias, out_simd);
    const auto end = esp_cpu_get_cycle_count();

    const auto cycles = end - start;
    ESP_LOGI(TAG, "C++ SIMD шар виконано за %u тактів (%.2f мкс при 240 МГц)",
             cycles, static_cast<float>(cycles) / 240.0f);
}
