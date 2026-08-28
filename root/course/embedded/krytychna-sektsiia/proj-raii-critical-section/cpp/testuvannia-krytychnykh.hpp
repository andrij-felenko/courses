#pragma once

#include <cstdint>
#include <atomic>

namespace embedded::mock {

class HostMockLockPolicy {
public:
    using StateType = std::uint32_t;

    static inline std::atomic<std::uint32_t> lock_count{0};
    static inline std::atomic<bool> is_locked{false};

    [[nodiscard]] static StateType enter() noexcept {
        const StateType prev = is_locked.exchange(true) ? 1U : 0U;
        ++lock_count;
        return prev;
    }

    static void exit(StateType state) noexcept {
        is_locked.store(state != 0U);
    }

    static void reset() noexcept {
        lock_count.store(0);
        is_locked.store(false);
    }
};

} // namespace embedded::mock
