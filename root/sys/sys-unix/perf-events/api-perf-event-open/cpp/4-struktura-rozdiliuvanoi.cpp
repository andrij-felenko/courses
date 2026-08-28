// Зчитування data_head у C++20 з використанням std::atomic_load_explicit
#include <linux/perf_event.h>
#include <atomic>
#include <cstdint>

namespace sys {
    inline std::uint64_t read_ring_buffer_head(const perf_event_mmap_page* page) noexcept {
        return std::atomic_load_explicit(
            reinterpret_cast<const std::atomic<std::uint64_t>*>(&page->data_head),
            std::memory_order_acquire
        );
    }
}
