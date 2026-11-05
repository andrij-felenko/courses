#include <atomic>
#include <cstdint>
#include <cstring>

struct alignas(4) DeviceState {
    uint16_t status_flags;
    uint16_t sequence_number;
};

class LockFreeStateController {
public:
    explicit LockFreeStateController(uint16_t initial_flags = 0) noexcept {
        DeviceState init_state{initial_flags, 0};
        state_raw_.store(to_raw(init_state), std::memory_order_relaxed);
    }

    // Безблокувальне оновлення прапорців статусу
    void update_flags(uint16_t set_mask, uint16_t clear_mask) noexcept {
        uint32_t expected = state_raw_.load(std::memory_order_relaxed);
        uint32_t desired = 0;

        do {
            DeviceState current = from_raw(expected);
            current.status_flags = (current.status_flags & ~clear_mask) | set_mask;
            current.sequence_number++;
            desired = to_raw(current);
        } while (!state_raw_.compare_exchange_weak(
            expected,
            desired,
            std::memory_order_release,
            std::memory_order_relaxed));
    }

    DeviceState get_state() const noexcept {
        uint32_t raw = state_raw_.load(std::memory_order_acquire);
        return from_raw(raw);
    }

private:
    static uint32_t to_raw(DeviceState s) noexcept {
        uint32_t raw = 0;
        std::memcpy(&raw, &s, sizeof(raw));
        return raw;
    }

    static DeviceState from_raw(uint32_t raw) noexcept {
        DeviceState s{};
        std::memcpy(&s, &raw, sizeof(s));
        return s;
    }

    std::atomic<uint32_t> state_raw_{0};
};
