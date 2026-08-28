#include <atomic>
#include <cstdint>

// У C++20 стандартні атоміки безпосередньо транслюються в LDREX/STREX
class AtomicPacketCounter {
public:
    void increment() noexcept {
        // Компілятор транслює fetch_add у цикл з LDREX / STREX
        counter_.fetch_add(1, std::memory_order_relaxed);
    }

    [[nodiscard]] std::uint32_t get() const noexcept {
        return counter_.load(std::memory_order_relaxed);
    }

private:
    std::atomic<std::uint32_t> counter_{0};
};
