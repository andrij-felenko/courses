#include <span>
#include <array>
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// Обгортка RAII для м'ютекса FreeRTOS
class RtosMutexGuard {
public:
    explicit RtosMutexGuard(SemaphoreHandle_t mtx, TickType_t timeout = portMAX_DELAY)
        : mutex_(mtx), acquired_(xSemaphoreTake(mtx, timeout) == pdTRUE) {}

    ~RtosMutexGuard() {
        if (acquired_) {
            xSemaphoreGive(mutex_);
        }
    }

    [[nodiscard]] bool is_locked() const noexcept { return acquired_; }

    RtosMutexGuard(const RtosMutexGuard&) = delete;
    RtosMutexGuard& operator=(const RtosMutexGuard&) = delete;

private:
    SemaphoreHandle_t mutex_;
    bool acquired_;
};

class PeriodicControlTask {
public:
    static constexpr size_t StackWords = 256;
    static constexpr TickType_t PeriodTicks = pdMS_TO_TICKS(1);

    PeriodicControlTask() noexcept {
        mutex_handle_ = xSemaphoreCreateMutexStatic(&mutex_buffer_);
        task_handle_ = xTaskCreateStatic(
            &PeriodicControlTask::task_entry,
            "ControlTaskCpp",
            StackWords,
            this,
            configMAX_PRIORITIES - 1,
            stack_storage_.data(),
            &task_buffer_
        );
    }

private:
    static void task_entry(void* param) {
        static_cast<PeriodicControlTask*>(param)->run();
    }

    void run() {
        TickType_t last_wake_time = xTaskGetTickCount();

        for (;;) {
            vTaskDelayUntil(&last_wake_time, PeriodTicks);

            RtosMutexGuard lock(mutex_handle_, pdMS_TO_TICKS(0));
            if (lock.is_locked()) {
                // Детермінований обчислювальний крок
                perform_control_step();
            }
        }
    }

    void perform_control_step() noexcept {
        // Логіка оновлення приводу
    }

    std::array<StackType_t, StackWords> stack_storage_{};
    StaticTask_t task_buffer_{};
    StaticSemaphore_t mutex_buffer_{};
    SemaphoreHandle_t mutex_handle_{nullptr};
    TaskHandle_t task_handle_{nullptr};
};

static PeriodicControlTask global_control_task;
