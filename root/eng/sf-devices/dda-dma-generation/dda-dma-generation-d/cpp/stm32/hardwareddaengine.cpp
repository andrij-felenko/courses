#include "stm32f7xx_hal.h"
#include "FreeRTOS.h"
#include "task.h"
#include <cstdint>
#include <array>
#include <atomic>

namespace motion {

class HardwareDdaEngine {
public:
    static constexpr size_t kHalfSize = 1000;
    static constexpr size_t kFullSize = kHalfSize * 2;

    static constexpr uint32_t kStepPinSet   = (1U << 0);
    static constexpr uint32_t kStepPinReset = (1U << 16);
    static constexpr uint32_t kDirPinSet    = (1U << 1);
    static constexpr uint32_t kDirPinReset  = (1U << 17);

    HardwareDdaEngine(TIM_HandleTypeDef& htim, DMA_HandleTypeDef& hdma, GPIO_TypeDef* gpio_port)
        : htim_(htim), hdma_(hdma), port_(gpio_port) {}

    void Initialize() {
        // Початкова підготовка первинних патернів руху
        FillHalfBuffer(0, current_direction_);
        FillHalfBuffer(kHalfSize, current_direction_);
        lower_ready_.store(true, std::memory_order_release);
        upper_ready_.store(true, std::memory_order_release);

        worker_task_handle_ = xTaskGetCurrentTaskHandle();

        // Ініціалізація кільцевого циклічного вивантаження DMA
        HAL_DMA_Start_IT(&hdma_, 
                         reinterpret_cast<uint32_t>(dma_buffer_.data()), 
                         reinterpret_cast<uint32_t>(&(port_->BSRR)), 
                         kFullSize);

        __HAL_TIM_ENABLE_DMA(&htim_, TIM_DMA_UPDATE);
        HAL_TIM_Base_Start(&htim_);
    }

    void HandleHalfTransferIsr() {
        BaseType_t higher_woken = pdFALSE;
        lower_ready_.store(false, std::memory_order_relaxed);

        if (worker_task_handle_ != nullptr) {
            vTaskNotifyGiveFromISR(worker_task_handle_, &higher_woken);
            portYIELD_FROM_ISR(higher_woken);
        }
    }

    void HandleTransferCompleteIsr() {
        BaseType_t higher_woken = pdFALSE;
        upper_ready_.store(false, std::memory_order_relaxed);

        if (worker_task_handle_ != nullptr) {
            vTaskNotifyGiveFromISR(worker_task_handle_, &higher_woken);
            portYIELD_FROM_ISR(higher_woken);
        }
    }

    void ProcessBackgroundUpdates() {
        if (!lower_ready_.load(std::memory_order_acquire)) {
            FillHalfBuffer(0, current_direction_);
            lower_ready_.store(true, std::memory_order_release);
        }

        if (!upper_ready_.load(std::memory_order_acquire)) {
            FillHalfBuffer(kHalfSize, current_direction_);
            upper_ready_.store(true, std::memory_order_release);
        }
    }

private:
    void FillHalfBuffer(size_t offset, bool direction) {
        for (size_t i = 0; i < kHalfSize; ++i) {
            uint32_t mask = 0;

            if (direction != last_direction_) {
                mask |= direction ? kDirPinSet : kDirPinReset;
                last_direction_ = direction;
                dma_buffer_[offset + i] = mask;
                continue;
            }

            mask |= direction ? kDirPinSet : kDirPinReset;

            if (i % 20 == 0) {
                mask |= kStepPinSet;
            } else if (i % 20 == 2) {
                mask |= kStepPinReset;
            }

            dma_buffer_[offset + i] = mask;
        }

        // Очищення кешу пам'яті для гарантування когерентності
        SCB_CleanDCache_by_Addr(reinterpret_cast<uint32_t*>(&dma_buffer_[offset]), 
                                kHalfSize * sizeof(uint32_t));
        __DMB();
    }

    TIM_HandleTypeDef& htim_;
    DMA_HandleTypeDef& hdma_;
    GPIO_TypeDef* port_;

    alignas(32) std::array<uint32_t, kFullSize> dma_buffer_{};
    std::atomic<bool> lower_ready_{false};
    std::atomic<bool> upper_ready_{false};
    TaskHandle_t worker_task_handle_{nullptr};
    bool current_direction_{true};
    bool last_direction_{true};
};

} // namespace motion
