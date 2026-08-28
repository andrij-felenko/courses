#include <iostream>
#include <thread>
#include <vector>
#include <atomic>
#include <cstdint>
#include <chrono>

struct alignas(64) StressHarness {
    // Навмисне невирівняне поле для провокації розриву кеш-лінії
    struct alignas(1) UnalignedSlot {
        char pad[61];
        uint64_t raw_value;
    } unaligned;

    // Альтернативне коректне атомарне поле для порівняння
    std::atomic<uint64_t> safe_value{0};
    std::atomic<bool> running{true};
    std::atomic<uint64_t> torn_reads_detected{0};
};

void run_writer(StressHarness& harness, uint64_t iterations) {
    constexpr uint64_t val_a = 0x0000000000000000ULL;
    constexpr uint64_t val_b = 0xFFFFFFFFFFFFFFFFULL;

    for (uint64_t i = 0; i < iterations && harness.running.load(std::memory_order_relaxed); ++i) {
        harness.unaligned.raw_value = (i & 1) ? val_a : val_b;
    }
    harness.running.store(false, std::memory_order_relaxed);
}

void run_reader(StressHarness& harness) {
    constexpr uint64_t val_a = 0x0000000000000000ULL;
    constexpr uint64_t val_b = 0xFFFFFFFFFFFFFFFFULL;
    uint64_t local_anomalies = 0;

    while (harness.running.load(std::memory_order_relaxed)) {
        uint64_t observed = harness.unaligned.raw_value;
        if (observed != val_a && observed != val_b) {
            local_anomalies++;
        }
    }

    harness.torn_reads_detected.fetch_add(local_anomalies, std::memory_order_relaxed);
}

int main() {
    StressHarness harness{};
    constexpr uint64_t test_iterations = 100'000'000ULL;
    constexpr size_t num_readers = 4;

    std::cout << "Запуск багатопотокового аналізу розривних звернень..." << std::endl;

    std::vector<std::jthread> reader_pool;
    reader_pool.reserve(num_readers);
    for (size_t i = 0; i < num_readers; ++i) {
        reader_pool.emplace_back(run_reader, std::ref(harness));
    }

    std::jthread writer(run_writer, std::ref(harness), test_iterations);
    writer.join();

    for (auto& reader : reader_pool) {
        reader.join();
    }

    std::cout << "Аналіз завершено. Кількість розривних станів: "
              << harness.torn_reads_detected.load() << std::endl;

    return 0;
}
