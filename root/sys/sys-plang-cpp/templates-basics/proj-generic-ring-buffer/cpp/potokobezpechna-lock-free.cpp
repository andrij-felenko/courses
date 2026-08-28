#include <atomic>
#include <new>

template <typename T, std::size_t Capacity>
class LockFreeSPSCQueue {
    static_assert(Capacity > 0 && ((Capacity & (Capacity - 1)) == 0),
                  "Розмір Lock-Free черги зобов'язаний бути степенем двійки!");

public:
    LockFreeSPSCQueue() : head_(0), tail_(0) {}

    ~LockFreeSPSCQueue() {
        T dummy;
        while (pop(dummy)) {}
    }

    // Викликається винятково потоком-виробником (Producer)
    bool push(const T& item) {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        const size_t current_head = head_.load(std::memory_order_acquire);

        if ((current_tail - current_head) == Capacity) {
            return false; // Черга заповнена
        }

        ::new (static_cast<void*>(&storage_[(current_tail & (Capacity - 1)) * sizeof(T)])) T(item);
        tail_.store(current_tail + 1, std::memory_order_release);
        return true;
    }

    // Викликається винятково потоком-споживачем (Consumer)
    bool pop(T& item) {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t current_tail = tail_.load(std::memory_order_acquire);

        if (current_head == current_tail) {
            return false; // Черга порожня
        }

        T* ptr = reinterpret_cast<T*>(&storage_[(current_head & (Capacity - 1)) * sizeof(T)]);
        item = std::move(*ptr);
        ptr->~T();

        head_.store(current_head + 1, std::memory_order_release);
        return true;
    }

private:
    alignas(alignof(T)) std::byte storage_[Capacity * sizeof(T)];

    // Розділення індексів на різні кеш-лінії для запобігання False Sharing (64 байти)
    alignas(64) std::atomic<std::size_t> head_{0};
    alignas(64) std::atomic<std::size_t> tail_{0};
};
