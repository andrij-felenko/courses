#include <cstdint>
#include <cstddef>
#include <array>

namespace sys {

// RAII-обгортка для низькорівневого маскування переривань
class CriticalGuard final {
public:
    CriticalGuard() noexcept {
        __asm__ __volatile__(
            "mrs %0, basepri \n\t"
            "msr basepri, %1 \n\t"
            "isb             \n\t"
            : "=r"(saved_mask_)
            : "r"(0x20)
            : "memory"
        );
    }

    ~CriticalGuard() noexcept {
        __asm__ __volatile__(
            "msr basepri, %0 \n\t"
            "isb             \n\t"
            :
            : "r"(saved_mask_)
            : "memory"
        );
    }

    // Забороняємо копіювання та переміщення об'єкта
    CriticalGuard(const CriticalGuard&) = delete;
    CriticalGuard& operator=(const CriticalGuard&) = delete;
    CriticalGuard(CriticalGuard&&) = delete;
    CriticalGuard& operator=(CriticalGuard&&) = delete;

private:
    std::uint32_t saved_mask_{0};
};

// Потокобезпечний кільцевий буфер C++
template <typename T, std::size_t N>
class SafeRingBuffer {
public:
    bool push(const T& item) noexcept {
        CriticalGuard lock; // RAII-захист критичного блоку
        
        std::size_t next_head = (head_ + 1) % N;
        if (next_head == tail_) {
            return false;
        }
        
        buffer_[head_] = item;
        head_ = next_head;
        return true;
    }

private:
    std::array<T, N> buffer_{};
    volatile std::size_t head_{0};
    volatile std::size_t tail_{0};
};

} // namespace sys
