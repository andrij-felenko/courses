// cpp
#include <atomic>
#include <cstdint>
#include <span>

struct IoUringBufRingHelper {
    IoUringBuf* bufs;
    std::uint16_t* tail_ptr;

    void add(void* addr, std::uint32_t len, std::uint16_t bid, std::uint16_t mask, int offset) noexcept {
        std::uint16_t current_tail = *tail_ptr;
        auto& buf = bufs[(current_tail + offset) & mask];
        buf.addr = reinterpret_cast<std::uint64_t>(addr);
        buf.len = len;
        buf.bid = bid;
    }

    void advance(std::uint16_t count) noexcept {
        auto* atomic_tail = reinterpret_cast<std::atomic<std::uint16_t>*>(tail_ptr);
        atomic_tail->fetch_add(count, std::memory_order_release);
    }
};
