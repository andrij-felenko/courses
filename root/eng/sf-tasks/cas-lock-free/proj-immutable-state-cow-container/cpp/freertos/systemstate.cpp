#include <atomic>
#include <cstdint>
#include <array>
#include <cstring>

struct SystemState {
    uint32_t sample_rate_hz;
    uint16_t gain_dB;
    uint16_t filter_cutoff_hz;
    uint32_t update_sequence;
};

class LockFreeStateContainer {
public:
    static constexpr size_t PoolSize = 3;

    struct alignas(8) StateRef {
        uint32_t index;
        uint32_t generation;
    };

    LockFreeStateContainer() {
        StateRef init_ref{0, 0};
        uint64_t packed;
        std::memcpy(&packed, &init_ref, sizeof(packed));
        packed_ref_.store(packed, std::memory_order_relaxed);
    }

    // Зчитування стану без блокувань із гарантією Wait-Free
    SystemState read() const {
        uint64_t packed = packed_ref_.load(std::memory_order_acquire);
        StateRef ref;
        std::memcpy(&ref, &packed, sizeof(ref));
        return pool_[ref.index % PoolSize];
    }

    // Модифікація стану в циклі CAS із семантикою Lock-Free
    bool update(const SystemState& new_state, uint32_t max_retries = 8) {
        uint64_t expected_packed = packed_ref_.load(std::memory_order_relaxed);

        for (uint32_t retry = 0; retry < max_retries; ++retry) {
            StateRef expected_ref;
            std::memcpy(&expected_ref, &expected_packed, sizeof(expected_ref));

            uint32_t next_index = (expected_ref.index + 1) % PoolSize;
            pool_[next_index] = new_state;
            pool_[next_index].update_sequence = expected_ref.generation + 1;

            StateRef desired_ref{next_index, expected_ref.generation + 1};
            uint64_t desired_packed;
            std::memcpy(&desired_packed, &desired_ref, sizeof(desired_packed));

            if (packed_ref_.compare_exchange_weak(
                    expected_packed, desired_packed,
                    std::memory_order_release,
                    std::memory_order_relaxed)) {
                return true; // Атомарна підміна успішна
            }
        }
        return false; // Перевищено ліміт спроб
    }

private:
    std::array<SystemState, PoolSize> pool_{};
    alignas(8) std::atomic<uint64_t> packed_ref_{0};
};
