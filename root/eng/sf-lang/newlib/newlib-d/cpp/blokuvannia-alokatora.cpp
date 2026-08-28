#include <sys/reent.h>
#include <span>
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

namespace rtos {

class MallocLockGuard {
public:
    static void init() noexcept {
        if (mutex_handle_ == nullptr) {
            mutex_handle_ = xSemaphoreCreateMutexStatic(&mutex_buffer_);
        }
    }

    static void lock() noexcept {
        if (xTaskGetSchedulerState() != taskSCHEDULER_NOT_STARTED && mutex_handle_ != nullptr) {
            xSemaphoreTake(mutex_handle_, portMAX_DELAY);
        }
    }

    static void unlock() noexcept {
        if (xTaskGetSchedulerState() != taskSCHEDULER_NOT_STARTED && mutex_handle_ != nullptr) {
            xSemaphoreGive(mutex_handle_);
        }
    }

private:
    static inline SemaphoreHandle_t mutex_handle_{nullptr};
    static inline StaticSemaphore_t mutex_buffer_{};
};

} // namespace rtos

extern "C" {

void __malloc_lock(struct _reent * /*r*/) {
    rtos::MallocLockGuard::lock();
}

void __malloc_unlock(struct _reent * /*r*/) {
    rtos::MallocLockGuard::unlock();
}

} // extern "C"
