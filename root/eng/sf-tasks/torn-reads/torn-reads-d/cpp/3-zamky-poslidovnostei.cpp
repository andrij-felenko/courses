#include <atomic>
#include <cstdint>

struct TelemetryRecord {
    std::atomic<uint32_t> sequence{0};
    uint64_t x{0};
    uint64_t y{0};
    uint64_t z{0};

    TelemetryRecord read_snapshot() const noexcept {
        TelemetryRecord result;
        uint32_t seq = 0;
        do {
            seq = sequence.load(std::memory_order_acquire);
            while (seq & 1) { // Непарний стан — іде активний запис
                seq = sequence.load(std::memory_order_acquire);
            }
            result.x = x;
            result.y = y;
            result.z = z;
        } while (sequence.load(std::memory_order_acquire) != seq);
        return result;
    }
};
