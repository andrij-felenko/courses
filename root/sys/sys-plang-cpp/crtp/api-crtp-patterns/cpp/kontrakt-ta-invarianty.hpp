#include <atomic>

template <typename Derived>
class ThreadSafeCounter {
public:
    ThreadSafeCounter() noexcept {
        counter_.fetch_add(1, std::memory_order_relaxed);
    }

    ThreadSafeCounter(const ThreadSafeCounter&) noexcept {
        counter_.fetch_add(1, std::memory_order_relaxed);
    }

    ThreadSafeCounter(ThreadSafeCounter&&) noexcept {
        counter_.fetch_add(1, std::memory_order_relaxed);
    }

    ~ThreadSafeCounter() noexcept {
        counter_.fetch_sub(1, std::memory_order_relaxed);
    }

    static size_t active_instances() noexcept {
        return counter_.load(std::memory_order_relaxed);
    }

private:
    inline static std::atomic<size_t> counter_{0};
};

class ConnectionHandle : public ThreadSafeCounter<ConnectionHandle> {};
class DatabaseSession : public ThreadSafeCounter<DatabaseSession> {};
