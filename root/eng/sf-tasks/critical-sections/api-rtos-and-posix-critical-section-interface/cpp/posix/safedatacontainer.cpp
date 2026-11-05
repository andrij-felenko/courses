#include <pthread.h>
#include <mutex>
#include <cstdint>

class SafeDataContainer {
private:
    mutable std::mutex mutex_;
    uint64_t data_value_{0};

public:
    void update_value(uint64_t new_val) {
        /* Використання std::lock_guard для гарантованого звільнення м'ютекса */
        std::lock_guard<std::mutex> lock(mutex_);
        data_value_ += new_val;
    }

    uint64_t get_value() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return data_value_;
    }
};
