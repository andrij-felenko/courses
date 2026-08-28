#include <stdatomic.h>
#include <stdint.h>

_Atomic uint64_t telemetry_counter = 0;

void producer(uint64_t val) {
    atomic_store_explicit(&telemetry_counter, val, memory_order_relaxed);
}

uint64_t consumer(void) {
    return atomic_load_explicit(&telemetry_counter, memory_order_relaxed);
}
