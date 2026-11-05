#include <atomic>
#include <cstdint>

class StateManager {
private:
    std::atomic<uint32_t> state_;

public:
    explicit StateManager(uint32_t initial_val = 0) noexcept : state_(initial_val) {}

    // Безблокувальне оновлення стану з використанням std::atomic::compare_exchange_weak
    uint32_t update(uint32_t addend) noexcept {
        uint32_t expected = state_.load(std::memory_order_relaxed);
        uint32_t desired = 0;

        do {
            desired = expected + addend;
            // У разі відмови expected автоматично оновлюється поточним значенням state_
        } while (!state_.compare_exchange_weak(
            expected,
            desired,
            std::memory_order_release,
            std::memory_order_relaxed));

        return desired;
    }

    [[nodiscard]] uint32_t get_state() const noexcept {
        return state_.load(std::memory_order_acquire);
    }
};
