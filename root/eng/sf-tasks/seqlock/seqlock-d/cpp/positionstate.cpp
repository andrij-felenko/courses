#include <atomic>
#include <cstdint>
#include <utility>

struct PositionState {
    double x{0.0};
    double y{0.0};
    double z{0.0};
    std::uint64_t timestamp_ns{0};
};

class SeqlockPosition {
private:
    alignas(64) std::atomic<std::uint32_t> sequence_{0};
    PositionState state_;

public:
    SeqlockPosition() = default;

    // Письменник не блокується читачами та виконує впорядкований запис
    void update(double x, double y, double z, std::uint64_t ts) noexcept {
        const auto current_seq = sequence_.load(std::memory_order_relaxed);
        
        // Початок запису: непарне значення
        sequence_.store(current_seq + 1, std::memory_order_relaxed);
        std::atomic_thread_fence(std::memory_order_release);

        state_.x = x;
        state_.y = y;
        state_.z = z;
        state_.timestamp_ns = ts;

        // Завершення запису: парне значення
        sequence_.store(current_seq + 2, std::memory_order_release);
    }
};
