#include <mutex>

class ThreadSafeCache {
public:
    int get_value(int key) const {
        std::lock_guard<std::mutex> lock(mutex_); // mutex_ змінює стан, будучи mutable!
        return cached_value_;
    }

private:
    int cached_value_{0};
    mutable std::mutex mutex_; // Легальна зміна стану в const-контексті
};
