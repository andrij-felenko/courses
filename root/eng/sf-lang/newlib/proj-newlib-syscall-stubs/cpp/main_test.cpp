/**
 * @file main_test.cpp
 * @brief Тестовий стенд діагностики Newlib (C++20)
 */
#include "syscall_stubs.hpp"
#include <cstdio>
#include <vector>
#include <memory>
#include <numeric>
#include <cerrno>

namespace test {

void run_cpp_diagnostics() noexcept {
    using namespace embedded::sys;

    SyscallManager::initialize();

    std::printf("========================================\r\n");
    std::printf("     Newlib Embedded Diagnostics (C++20)\r\n");
    std::printf("========================================\r\n");

    // Тест 1: Перевірка чисел із рухомою комою
    const float temp = 24.85f;
    const double pressure = 1013.25;
    std::printf("[TEST 1] Float: T=%.2f C, P=%.2f hPa\r\n", static_cast<double>(temp), pressure);

    // Тест 2: Метрики пам'яті
    auto metrics = SyscallManager::get_metrics();
    std::printf("[TEST 2] Initial State:\r\n");
    std::printf("  - Heap Start:   0x%08lX\r\n", static_cast<unsigned long>(metrics.heap_start_addr));
    std::printf("  - Current SP:   0x%08lX\r\n", static_cast<unsigned long>(metrics.current_sp));
    std::printf("  - Free Margin:  %zu bytes\r\n", metrics.free_margin_bytes);

    // Тест 3: RAII та std::vector у Newlib
    {
        std::printf("[TEST 3] Testing std::vector allocation...\r\n");
        std::vector<int> numbers;
        numbers.reserve(100);
        for (int i = 0; i < 100; ++i) {
            numbers.push_back(i * 2);
        }
        const auto sum = std::accumulate(numbers.begin(), numbers.end(), 0);
        std::printf("  -> Vector sum (0..198): %d (Capacity: %zu)\r\n", sum, numbers.capacity());
    }
    std::printf("  -> Vector destroyed, memory returned to heap.\r\n");

    // Тест 4: Стрес-тест переповнення пам'яті
    std::printf("[TEST 4] Stress Testing Out-of-Memory handling...\r\n");
    std::vector<std::unique_ptr<std::uint8_t[]>> blocks;
    constexpr std::size_t BlockSize = 2048;
    std::size_t total_allocated{0};

    while (true) {
        auto* raw = static_cast<std::uint8_t*>(std::malloc(BlockSize));
        if (raw == nullptr) {
            std::printf("  -> Protection verified: malloc returned NULL, errno=%d\r\n", errno);
            break;
        }
        blocks.emplace_back(raw);
        total_allocated += BlockSize;
        if (blocks.size() > 100) break; // Запобіжник
    }

    std::printf("  -> Allocated %zu bytes across %zu blocks.\r\n", total_allocated, blocks.size());
    blocks.clear(); // Автоматичне звільнення всіх блоків

    const auto final_metrics = SyscallManager::get_metrics();
    std::printf("[TEST 5] Final Report:\r\n");
    std::printf("  - Allocation Failures: %zu\r\n", final_metrics.allocation_failures);
    std::printf("  - Free RAM Margin:     %zu bytes\r\n", final_metrics.free_margin_bytes);
    std::printf("========================================\r\n");
}

} // namespace test
