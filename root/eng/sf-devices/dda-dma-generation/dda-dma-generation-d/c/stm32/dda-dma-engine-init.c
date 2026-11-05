#include "stm32f4xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

#define DDA_BUFFER_HALF_SIZE 1000
#define DDA_BUFFER_FULL_SIZE (DDA_BUFFER_HALF_SIZE * 2)

// Буфер патернів GPIO: перша половина (0..999), друга половина (1000..1999)
static uint32_t dda_gpio_buffer[DDA_BUFFER_FULL_SIZE];

// Прапорці стану буферів для синхронізації з RTOS
volatile bool buffer_first_half_ready = false;
volatile bool buffer_second_half_ready = false;

extern TIM_HandleTypeDef htim1;
extern DMA_HandleTypeDef hdma_tim1_up;

// Ініціалізація автономної DMA-передачі патернів DDA у порт GPIO
void dda_dma_engine_init(void) {
    // Налаштування DMA у кільцевому режимі з оновленням регістра BSRR
    HAL_DMA_Start_IT(&hdma_tim1_up, 
                     (uint32_t)dda_gpio_buffer, 
                     (uint32_t)&(GPIOB->BSRR), 
                     DDA_BUFFER_FULL_SIZE);

    // Увімкнення генерації DMA-запитів при переповненні TIM1
    __HAL_TIM_ENABLE_DMA(&htim1, TIM_DMA_UPDATE);
    
    // Запуск апаратного таймера
    HAL_TIM_Base_Start(&htim1);
}

// Обробник переривання DMA: завершено вивантаження першої половини буфера (Half Transfer)
void HAL_DMA_XferHalfCpltCallback(DMA_HandleTypeDef *hdma) {
    if (hdma->Instance == DMA2_Stream5) {
        buffer_first_half_ready = false; // Позначити першу половину як вільну для запису CPU
        // Сповіщення RTOS-задачі про необхідність генерації нових квантів DDA
    }
}

// Обробник переривання DMA: завершено вивантаження другої половини буфера (Transfer Complete)
void HAL_DMA_XferCpltCallback(DMA_HandleTypeDef *hdma) {
    if (hdma->Instance == DMA2_Stream5) {
        buffer_second_half_ready = false; // Позначити другу половину як вільну для запису CPU
        // Сповіщення RTOS-задачі для поповнення другої половини
    }
}

// Заповнення вказаної секції буфера патернами DDA у фоновій задачі CPU
void dda_fill_buffer_section(uint32_t *start_ptr, uint32_t count) {
    for (uint32_t i = 0; i < count; i++) {
        uint32_t gpio_bsrr_val = 0;
        
        // Приклад розрахунку DDA для кроку осі X:
        // Маска 0x00010001 (SET Bit 0, RESET Bit 0) для формування імпульсу STEP
        if (i % 20 == 0) {
            gpio_bsrr_val |= (1 << 0);       // Встановити вивід STEP_X у HIGH
        } else if (i % 20 == 1) {
            gpio_bsrr_val |= (1 << (0 + 16));// Скинути вивід STEP_X у LOW
        }

        start_ptr[i] = gpio_bsrr_val;
    }
}
