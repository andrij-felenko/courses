#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

class ReentrantMutexGuard {
private:
    SemaphoreHandle_t& mutex_;
    bool locked_;

public:
    explicit ReentrantMutexGuard(SemaphoreHandle_t& mutex) : mutex_(mutex), locked_(false) {
        if (xSemaphoreTakeRecursive(mutex_, portMAX_DELAY) == pdTRUE) {
            locked_ = true;
        }
    }

    ~ReentrantMutexGuard() {
        if (locked_) {
            xSemaphoreGiveRecursive(mutex_);
        }
    }

    bool is_locked() const { return locked_; }
};

// Приклад використання в класі драйвера
class BusDriver {
private:
    SemaphoreHandle_t lock_handle_;

public:
    BusDriver() {
        lock_handle_ = xSemaphoreCreateRecursiveMutex();
    }

    void write_register(uint8_t reg, uint8_t val) {
        ReentrantMutexGuard guard(lock_handle_);
        // Апаратний запис у регістр
    }

    void safe_transaction() {
        ReentrantMutexGuard guard(lock_handle_);
        // Вкладений виклик використовує той самий реентрантний замок
        write_register(0x01, 0xFF);
    }
};
