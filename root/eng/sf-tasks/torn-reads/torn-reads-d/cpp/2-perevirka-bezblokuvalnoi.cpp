#include <atomic>
#include <cstdint>

// Перевірка на етапі компіляції:
static_assert(std::atomic<uint64_t>::is_always_lock_free);

bool check_hardware_support() {
    std::atomic<uint64_t> counter{0};
    return counter.is_lock_free();
}
