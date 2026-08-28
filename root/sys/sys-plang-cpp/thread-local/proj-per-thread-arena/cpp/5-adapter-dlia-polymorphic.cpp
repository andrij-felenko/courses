#include <memory_resource>

class ThreadLocalPmrResource : public std::pmr::memory_resource {
protected:
    void* do_allocate(std::size_t bytes, std::size_t alignment) override {
        return g_per_thread_arena.allocate(bytes, alignment);
    }

    void do_deallocate(void*, std::size_t, std::size_t) noexcept override {
        // Потоково-локальна арена не підтримує поодинокі звільнення
    }

    bool do_is_equal(const std::pmr::memory_resource& other) const noexcept override {
        // Два pmr-ресурси рівні, лише якщо вони вказують на той самий фізичний екземпляр
        return this == &other;
    }
};

// Глобальний доступ до pmr-ресурсу поточного потоку
inline thread_local ThreadLocalPmrResource g_thread_pmr_resource{};

std::pmr::memory_resource* get_thread_local_memory_resource() noexcept {
    return &g_thread_pmr_resource;
}
