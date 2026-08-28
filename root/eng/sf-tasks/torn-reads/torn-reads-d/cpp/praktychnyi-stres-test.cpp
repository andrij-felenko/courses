#include <iostream>
#include <thread>
#include <vector>
#include <atomic>
#include <cstdint>

struct alignas(64) BenchmarkContext {
    struct alignas(1) UnalignedTarget {
        char padding[60];
        uint64_t data_field;
    } target;

    std::atomic<uint64_t> safe_atomic_target{0};
    std::atomic<bool> is_running{true};
    std::atomic<uint64_t> torn_event_counter{0};
};

void execute_writer(BenchmarkContext& ctx, uint64_t limit) {
    constexpr uint64_t mask_zero = 0x0000000000000000ULL;
    constexpr uint64_t mask_full = 0xFFFFFFFFFFFFFFFFULL;

    for (uint64_t i = 0; i < limit && ctx.is_running.load(std::memory_order_relaxed); ++i) {
        ctx.target.data_field = (i & 1) ? mask_zero : mask_full;
    }
    ctx.is_running.store(false, std::memory_order_relaxed);
}

void execute_reader(BenchmarkContext& ctx) {
    constexpr uint64_t mask_zero = 0x0000000000000000ULL;
    constexpr uint64_t mask_full = 0xFFFFFFFFFFFFFFFFULL;
    uint64_t thread_torn_count = 0;

    while (ctx.is_running.load(std::memory_order_relaxed)) {
        uint64_t snapshot = ctx.target.data_field;
        if (snapshot != mask_zero && snapshot != mask_full) {
            thread_torn_count++;
        }
    }

    ctx.torn_event_counter.fetch_add(thread_torn_count, std::memory_order_relaxed);
}

int main() {
    BenchmarkContext ctx{};
    constexpr uint64_t total_iterations = 50'000'000ULL;
    constexpr size_t total_readers = 4;

    std::cout << "Запуск багатопотокового аналізу розривного читання..." << std::endl;

    std::vector<std::jthread> readers;
    readers.reserve(total_readers);
    for (size_t i = 0; i < total_readers; ++i) {
        readers.emplace_back(execute_reader, std::ref(ctx));
    }

    std::jthread writer(execute_writer, std::ref(ctx), total_iterations);
    writer.join();

    for (auto& reader : readers) {
        reader.join();
    }

    std::cout << "Підсумок: зафіксовано розривних читань: "
              << ctx.torn_event_counter.load() << std::endl;

    return 0;
}
