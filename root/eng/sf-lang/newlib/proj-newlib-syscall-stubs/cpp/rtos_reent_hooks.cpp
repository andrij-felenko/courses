/**
 * @file rtos_reent_hooks.cpp
 * @brief Інтеграція Newlib reentrancy з FreeRTOS (C++20)
 */
#include "syscall_stubs.hpp"
#include <sys/reent.h>
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

namespace embedded::sys::rtos {

class RtosSyncManager {
public:
    static void init() noexcept {
        if (mutex_ == nullptr) {
            mutex_ = xSemaphoreCreateMutexStatic(&mutex_storage_);
        }
    }

    static void lock() noexcept {
        if (xTaskGetSchedulerState() == taskSCHEDULER_RUNNING && mutex_ != nullptr) {
            xSemaphoreTake(mutex_, portMAX_DELAY);
        }
    }

    static void unlock() noexcept {
        if (xTaskGetSchedulerState() == taskSCHEDULER_RUNNING && mutex_ != nullptr) {
            xSemaphoreGive(mutex_);
        }
    }

private:
    static inline SemaphoreHandle_t mutex_{nullptr};
    static inline StaticSemaphore_t mutex_storage_{};
};

} // namespace embedded::sys::rtos

extern "C" {

void __malloc_lock(struct _reent * /*r*/) {
    embedded::sys::rtos::RtosSyncManager::lock();
}

void __malloc_unlock(struct _reent * /*r*/) {
    embedded::sys::rtos::RtosSyncManager::unlock();
}

} // extern "C"
