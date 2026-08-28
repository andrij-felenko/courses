/* C++ обгортка для шаблону Top-Half / Bottom-Half під FreeRTOS */
#include "FreeRTOS.h"
#include "task.h"
#include <optional>

class UartHandler {
public:
    static void init(TaskHandle_t task_handle) noexcept {
        processing_task_ = task_handle;
    }

    /* Верхня половина (викликається з extern "C" USART1_IRQHandler) */
    static void handle_isr() noexcept {
        BaseType_t higher_priority_task_woken = pdFALSE;

        if ((USART1->SR & USART_SR_RXNE) != 0) {
            const uint8_t byte = static_cast<uint8_t>(USART1->DR);
            
            // Запис у кільцевий буфер
            ring_buffer_.push_from_isr(byte);

            // Сповіщення нижньої половини
            if (processing_task_ != nullptr) {
                vTaskNotifyGiveFromISR(processing_task_, &higher_priority_task_woken);
            }

            portYIELD_FROM_ISR(higher_priority_task_woken);
        }
    }

private:
    static inline TaskHandle_t processing_task_{nullptr};
    static inline SpscRingBuffer<uint8_t, 256> ring_buffer_{};
};
