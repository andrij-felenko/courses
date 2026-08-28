#include <mutex>
#include <stdexcept>
#include <climits>
#include <cstdint>

class HierarchicalMutex {
public:
    explicit HierarchicalMutex(uint64_t hierarchy_value)
        : hierarchy_value_(hierarchy_value), previous_hierarchy_value_(0) {}

    void lock() {
        check_for_hierarchy_violation();
        internal_mutex_.lock();
        update_hierarchy_value();
    }

    void unlock() {
        if (this_thread_hierarchy_value_ != hierarchy_value_) {
            throw std::logic_error("Mutex hierarchy violated: unlocking out of order");
        }
        this_thread_hierarchy_value_ = previous_hierarchy_value_;
        internal_mutex_.unlock();
    }

    bool try_lock() {
        check_for_hierarchy_violation();
        if (!internal_mutex_.try_lock()) {
            return false;
        }
        update_hierarchy_value();
        return true;
    }

    uint64_t get_level() const noexcept { return hierarchy_value_; }

private:
    void check_for_hierarchy_violation() const {
        if (this_thread_hierarchy_value_ <= hierarchy_value_) {
            throw std::logic_error("Deadlock risk: mutex hierarchy violated! "
                                   "Attempting to acquire lock with higher or equal level.");
        }
    }

    void update_hierarchy_value() {
        previous_hierarchy_value_ = this_thread_hierarchy_value_;
        this_thread_hierarchy_value_ = hierarchy_value_;
    }

    std::mutex internal_mutex_;
    const uint64_t hierarchy_value_;
    uint64_t previous_hierarchy_value_;

    // Змінна потоку, що зберігає ранг останнього захопленого замка
    static thread_local uint64_t this_thread_hierarchy_value_;
};

// Початковий ранг для кожного нового потоку — максимальне можливе значення
thread_local uint64_t HierarchicalMutex::this_thread_hierarchy_value_(ULONG_MAX);
