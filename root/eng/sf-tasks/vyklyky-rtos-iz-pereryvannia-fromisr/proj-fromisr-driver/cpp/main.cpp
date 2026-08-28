#include <array>
#include <atomic>
#include <span>
#include <cstdint>
#include <concepts>

#include "FreeRTOS.h"
#include "task.h"

struct MockUsartRegs {
    volatile uint32_t sr;
    volatile uint32_t dr;
    volatile uint32_t cr1;
};

inline constexpr uint32_t USART_SR_RXNE = 1U << 5;
inline constexpr uint32_t USART_SR_ORE  = 1U << 3;
extern MockUsartRegs* USART1_REGS;

namespace drivers {

template <size_t BufferSize = 256>
requires ((BufferSize & (BufferSize - 1)) == 0) /* Розмір обов'язково є степенем двійки */
class UartDriver {
public:
    UartDriver() noexcept : head_(0), tail_(0), dropped_bytes_(0), worker_task_(nullptr) {}

    void register_worker(TaskHandle_t worker) noexcept {
        worker_task_ = worker;
    }

    /* Top-Half обробка в контексті ISR */
    void handle_irq() noexcept {
        BaseType_t higher_priority_task_woken = pdFALSE;
        const uint32_t status = USART1_REGS->sr;

        if (status & USART_SR_ORE) {
            [[maybe_unused]] volatile uint32_t dummy = USART1_REGS->dr;
            dropped_bytes_.fetch_add(1, std::memory_order_relaxed);
        }

        if (status & USART_SR_RXNE) {
            const uint8_t byte = static_cast<uint8_t>(USART1_REGS->dr & 0xFF);
            const size_t current_head = head_.load(std::memory_order_relaxed);
            const size_t next_head = (current_head + 1) & (BufferSize - 1);

            if (next_head != tail_.load(std::memory_order_acquire)) {
                buffer_[current_head] = byte;
                head_.store(next_head, std::memory_order_release);

                if (worker_task_ != nullptr) {
                    vTaskNotifyGiveFromISR(worker_task_, &higher_priority_task_woken);
                }
            } else {
                dropped_bytes_.fetch_add(1, std::memory_order_relaxed);
            }
        }

        portYIELD_FROM_ISR(higher_priority_task_woken);
    }

    /* Bottom-Half вичитка пакетів у задачі */
    [[nodiscard]] size_t read_available(std::span<uint8_t> output_buffer) noexcept {
        size_t bytes_read = 0;
        size_t current_tail = tail_.load(std::memory_order_relaxed);
        const size_t current_head = head_.load(std::memory_order_acquire);

        while (current_tail != current_head && bytes_read < output_buffer.size()) {
            output_buffer[bytes_read++] = buffer_[current_tail];
            current_tail = (current_tail + 1) & (BufferSize - 1);
        }

        tail_.store(current_tail, std::memory_order_release);
        return bytes_read;
    }

    [[nodiscard]] uint32_t get_and_reset_dropped() noexcept {
        return dropped_bytes_.exchange(0, std::memory_order_relaxed);
    }

private:
    std::array<uint8_t, BufferSize> buffer_{};
    std::atomic<size_t> head_;
    std::atomic<size_t> tail_;
    std::atomic<uint32_t> dropped_bytes_;
    TaskHandle_t worker_task_;
};

} // namespace drivers

static drivers::UartDriver<256> g_uart_driver;

extern "C" void USART1_IRQHandler() {
    g_uart_driver.handle_irq();
}

extern "C" void uart_worker_task(void* params) {
    (void)params;
    g_uart_driver.register_worker(xTaskGetCurrentTaskHandle());

    std::array<uint8_t, 32> local_batch{};

    for (;;) {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        size_t count = g_uart_driver.read_available(local_batch);
        for (size_t i = 0; i < count; ++i) {
            // process_protocol_byte(local_batch[i]);
        }
    }
}
