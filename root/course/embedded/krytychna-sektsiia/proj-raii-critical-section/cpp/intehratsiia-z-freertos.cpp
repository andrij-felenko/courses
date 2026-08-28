#include "critical_section.hpp"
#include "FreeRTOS.h"
#include "task.h"

namespace embedded::rtos {

class [[nodiscard]] FreeRtosGuard {
public:
    FreeRtosGuard() noexcept : is_isr_(sync::in_interrupt_context()) {
        if (is_isr_) {
            isr_saved_state_ = taskENTER_CRITICAL_FROM_ISR();
        } else {
            taskENTER_CRITICAL();
        }
    }

    ~FreeRtosGuard() noexcept {
        if (is_isr_) {
            taskEXIT_CRITICAL_FROM_ISR(isr_saved_state_);
        } else {
            taskEXIT_CRITICAL();
        }
    }

    FreeRtosGuard(const FreeRtosGuard&) = delete;
    FreeRtosGuard& operator=(const FreeRtosGuard&) = delete;

private:
    bool is_isr_{false};
    UBaseType_t isr_saved_state_{0};
};

} // namespace embedded::rtos
