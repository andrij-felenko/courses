#include <atomic>
#include <cstdint>

std::atomic<uint64_t> telemetry_counter{0};

void producer(uint64_t val) {
    telemetry_counter.store(val, std::memory_order_relaxed);
}

uint64_t consumer() {
    return telemetry_counter.load(std::memory_order_relaxed);
}
