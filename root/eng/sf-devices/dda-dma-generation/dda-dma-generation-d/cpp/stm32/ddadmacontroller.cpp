#include "stm32f4xx_hal.h"
#include <cstdint>
#include <array>

class DdaDmaController {
public:
    static constexpr size_t kHalfBufferSize = 1000;
    static constexpr size_t kFullBufferSize = kHalfBufferSize * 2;

    DdaDmaController(TIM_HandleTypeDef& htim, DMA_HandleTypeDef& hdma, GPIO_TypeDef* gpio_port)
        : htim_(htim), hdma_(hdma), gpio_port_(gpio_port) {}

    void Init() {
        // Запуск DMA пересилання у кільцевому режимі в регістр BSRR
        HAL_DMA_Start_IT(&hdma_, 
                         reinterpret_cast<uint32_t>(gpio_buffer_.data()), 
                         reinterpret_cast<uint32_t>(&(gpio_port_->BSRR)), 
                         kFullBufferSize);

        __HAL_TIM_ENABLE_DMA(&htim_, TIM_DMA_UPDATE);
        HAL_TIM_Base_Start(&htim_);
    }

    void OnHalfTransferComplete() {
        first_half_busy_ = false;
        // Сигналізація задачі розрахунку траєкторії
    }

    void OnTransferComplete() {
        second_half_busy_ = false;
        // Сигналізація задачі розрахунку траєкторії
    }

    void FillSection(size_t offset, size_t length) {
        for (size_t i = 0; i < length; ++i) {
            uint32_t bsrr_value = 0;
            // Обчислення стану виходів за алгоритмом DDA
            if ((i + offset) % 20 == 0) {
                bsrr_value |= (1 << 0);        // Set STEP pin HIGH
            } else if ((i + offset) % 20 == 1) {
                bsrr_value |= (1 << (0 + 16)); // Reset STEP pin LOW
            }
            gpio_buffer_[offset + i] = bsrr_value;
        }
    }

private:
    TIM_HandleTypeDef& htim_;
    DMA_HandleTypeDef& hdma_;
    GPIO_TypeDef* gpio_port_;
    
    alignas(4) std::array<uint32_t, kFullBufferSize> gpio_buffer_{};
    volatile bool first_half_busy_{true};
    volatile bool second_half_busy_{true};
};
