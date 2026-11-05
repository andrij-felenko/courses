#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

namespace Embedded {

class RecursiveMutex {
private:
    SemaphoreHandle_t handle_;
    StaticSemaphore_t buffer_;

public:
    RecursiveMutex() {
        handle_ = xSemaphoreCreateRecursiveMutexStatic(&buffer_);
    }

    ~RecursiveMutex() {
        if (handle_ != nullptr) {
            vSemaphoreDelete(handle_);
        }
    }

    // Заборона копіювання для збереження семантики унікального об'єкта
    RecursiveMutex(const RecursiveMutex&) = delete;
    RecursiveMutex& operator=(const RecursiveMutex&) = delete;

    bool lock(TickType_t timeout_ticks = portMAX_DELAY) {
        return xSemaphoreTakeRecursive(handle_, timeout_ticks) == pdTRUE;
    }

    void unlock() {
        xSemaphoreGiveRecursive(handle_);
    }
};

// RAII обгортка для гарантованого звільнення замка у C++
class RecursiveLockGuard {
private:
    RecursiveMutex& mutex_;
    bool acquired_;

public:
    explicit RecursiveLockGuard(RecursiveMutex& mutex, TickType_t timeout = portMAX_DELAY)
        : mutex_(mutex), acquired_(false) {
        acquired_ = mutex_.lock(timeout);
    }

    ~RecursiveLockGuard() {
        if (acquired_) {
            mutex_.unlock();
        }
    }

    // Перевірка успішності захоплення
    bool is_locked() const {
        return acquired_;
    }

    // Заборона переміщення та копіювання
    RecursiveLockGuard(const RecursiveLockGuard&) = delete;
    RecursiveLockGuard& operator=(const RecursiveLockGuard&) = delete;
};

} // namespace Embedded
