#include <atomic>

template <class T>
struct ControlBlock {
    T*                obj;
    std::atomic<long> strong;   // скільки Shared
    std::atomic<long> weak;     // скільки Weak + 1, поки strong > 0

    explicit ControlBlock(T* p)
        : obj(p), strong(1), weak(1) {}   // +1 — спільний токен сильних

    void retain() {
        strong.fetch_add(1, std::memory_order_relaxed);
    }

    void release() {
        if (strong.fetch_sub(1, std::memory_order_release) == 1) {
            std::atomic_thread_fence(std::memory_order_acquire);
            delete obj; obj = nullptr;         // об'єкт мертвий
            weak_release();                     // віддати спільний токен сильних
        }
    }

    void weak_retain() {
        weak.fetch_add(1, std::memory_order_relaxed);
    }

    void weak_release() {                       // ЄДИНИЙ власник рішення «звільнити блок»
        if (weak.fetch_sub(1, std::memory_order_release) == 1) {
            std::atomic_thread_fence(std::memory_order_acquire);
            delete this;
        }
    }
};
