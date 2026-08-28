#include <atomic>
#include <cstdint>

// Атомарні змінні C++20
inline std::atomic<std::uint32_t> g_atomic_counter{0};
inline std::atomic<bool> g_atomic_flag{false};

// Перевірка на етапі компіляції: чи є тип апаратно-безблокувальним
static_assert(std::atomic<std::uint32_t>::is_always_lock_free, 
              "std::atomic<uint32_t> must be hardware lock-free!");

void update_counter() noexcept {
    // Атомарне додавання без блокування переривань
    g_atomic_counter.fetch_add(1, std::memory_order_relaxed);
    
    // Публікація результату з бар'єром звільнення (Release semantics)
    g_atomic_flag.store(true, std::memory_order_release);
}

[[nodiscard]] bool check_and_clear_flag() noexcept {
    // Зчитування з бар'єром захоплення (Acquire semantics)
    return g_atomic_flag.exchange(false, std::memory_order_acquire);
}
