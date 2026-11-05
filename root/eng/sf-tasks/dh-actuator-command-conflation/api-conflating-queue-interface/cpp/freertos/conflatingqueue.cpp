#include <cstdint>
#include <array>
#include <atomic>
#include "FreeRTOS.h"
#include "task.h"

template <typename CommandType, std::size_t ActuatorCount>
class ConflatingQueue {
public:
    struct Slot {
        CommandType command;
        std::atomic<bool> is_pending{false};
    };

    explicit ConflatingQueue(TaskHandle_t driver_task = nullptr)
        : driver_task_handle_(driver_task) {}

    void set_driver_task(TaskHandle_t driver_task) {
        driver_task_handle_ = driver_task;
    }

    /* Вставка з автоматичним згортанням застарілих даних */
    bool push(std::size_t actuator_id, const CommandType& cmd) {
        if (actuator_id >= ActuatorCount) {
            return false;
        }

        UBaseType_t status = taskENTER_CRITICAL_FROM_ISR();
        slots_[actuator_id].command = cmd;
        slots_[actuator_id].is_pending.store(true, std::memory_order_release);
        taskEXIT_CRITICAL_FROM_ISR(status);

        if (driver_task_handle_ != nullptr) {
            BaseType_t higher_woken = pdFALSE;
            vTaskNotifyGiveFromISR(driver_task_handle_, &higher_woken);
            portYIELD_FROM_ISR(higher_woken);
        }

        return true;
    }

    /* Вибірка найсвіжішої команди драйвером */
    bool pop(std::size_t actuator_id, CommandType& out_cmd) {
        if (actuator_id >= ActuatorCount) {
            return false;
        }

        taskENTER_CRITICAL();
        bool pending = slots_[actuator_id].is_pending.load(std::memory_order_acquire);
        if (pending) {
            out_cmd = slots_[actuator_id].command;
            slots_[actuator_id].is_pending.store(false, std::memory_order_release);
        }
        taskEXIT_CRITICAL();

        return pending;
    }

private:
    std::array<Slot, ActuatorCount> slots_;
    TaskHandle_t driver_task_handle_{nullptr};
};
