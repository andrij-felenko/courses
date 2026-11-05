#include "stm32f7xx_hal.h"
#include "FreeRTOS.h"
#include "task.h"
#include <stdint.h>
#include <stdbool.h>

#define DDA_HALF_BUFFER_SIZE  1000
#define DDA_FULL_BUFFER_SIZE  (DDA_HALF_BUFFER_SIZE * 2)

// Маски виводів кроку та напрямку для осі X на порті GPIOB
#define STEP_PIN_SET_MASK     (1U << 0)
#define STEP_PIN_RESET_MASK   (1U << (0 + 16))
#define DIR_PIN_SET_MASK      (1U << 1)
#define DIR_PIN_RESET_MASK    (1U << (1 + 16))

// Буфер вирівняно за розміром рядка кешу (32 байти)
__attribute__((aligned(32))) 
static uint32_t dda_gpio_dma_buffer[DDA_FULL_BUFFER_SIZE];

static TaskHandle_t s_dda_worker_task_handle = NULL;
static volatile bool s_lower_half_busy = false;
static volatile bool s_upper_half_busy = false;

extern TIM_HandleTypeDef htim1;
extern DMA_HandleTypeDef hdma_tim1_up;

// Налаштування MPU: задання атрибутів некешованої пам'яті для буфера DMA
void dda_configure_mpu_region(void) {
    MPU_Region_InitTypeDef mpu_init;
    HAL_MPU_Disable();

    mpu_init.Enable           = MPU_REGION_ENABLE;
    mpu_init.Number           = MPU_REGION_NUMBER0;
    mpu_init.BaseAddress      = (uint32_t)dda_gpio_dma_buffer;
    mpu_init.Size             = MPU_REGION_SIZE_8KB;
    mpu_init.SubRegionDisable = 0x00;
    mpu_init.TypeExtField     = MPU_TEX_LEVEL1;
    mpu_init.AccessPermission = MPU_REGION_FULL_ACCESS;
    mpu_init.DisableExec      = MPU_INSTRUCTION_ACCESS_DISABLE;
    mpu_init.IsShareable      = MPU_ACCESS_NOT_SHAREABLE;
    mpu_init.IsCacheable      = MPU_ACCESS_NOT_CACHEABLE;
    mpu_init.IsBufferable     = MPU_ACCESS_NOT_BUFFERABLE;

    HAL_MPU_ConfigRegion(&mpu_init);
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
}

// Заповнення секції буфера патернами з дотриманням часу встановлення DIR
void dda_fill_buffer_section(uint32_t *target_buffer, size_t length, bool current_dir, bool *prev_dir) {
    for (size_t i = 0; i < length; ++i) {
        uint32_t bsrr_word = 0;

        // Перевірка зміни напрямку для вставки захисного кванта (dead time)
        if (current_dir != *prev_dir) {
            bsrr_word |= current_dir ? DIR_PIN_SET_MASK : DIR_PIN_RESET_MASK;
            *prev_dir = current_dir;
            // У цьому кванті імпульс STEP не виставляється
            target_buffer[i] = bsrr_word;
            continue;
        }

        // Забезпечення постійного стану лінії напрямку
        bsrr_word |= current_dir ? DIR_PIN_SET_MASK : DIR_PIN_RESET_MASK;

        // Генерація кроку DDA: активний рівень HIGH на кожному 20-му кванті
        if (i % 20 == 0) {
            bsrr_word |= STEP_PIN_SET_MASK;
        } else if (i % 20 == 2) { // Тривалість імпульсу 2 кванти (4 мкс при кванті 2 мкс)
            bsrr_word |= STEP_PIN_RESET_MASK;
        }

        target_buffer[i] = bsrr_word;
    }

    // Примусове виштовхування кеш-рядків у пам'ять, якщо MPU не активовано
    SCB_CleanDCache_by_Addr(target_buffer, length * sizeof(uint32_t));
    __DMB(); // Бар'єр пам'яті: завершити всі транзакції до зміни стану
}

// Обробник половинної передачі DMA: звільнилася нижня половина буфера
void HAL_DMA_HalfTransferCallback(DMA_HandleTypeDef *hdma) {
    BaseType_t higher_priority_task_woken = pdFALSE;
    s_lower_half_busy = false;

    if (s_dda_worker_task_handle != NULL) {
        vTaskNotifyGiveFromISR(s_dda_worker_task_handle, &higher_priority_task_woken);
        portYIELD_FROM_ISR(higher_priority_task_woken);
    }
}

// Обробник повного завершення передачі DMA: звільнилася верхня половина буфера
void HAL_DMA_TransferCompleteCallback(DMA_HandleTypeDef *hdma) {
    BaseType_t higher_priority_task_woken = pdFALSE;
    s_upper_half_busy = false;

    if (s_dda_worker_task_handle != NULL) {
        vTaskNotifyGiveFromISR(s_dda_worker_task_handle, &higher_priority_task_woken);
        portYIELD_FROM_ISR(higher_priority_task_woken);
    }
}

// Задача операційної системи для підготовки блоків траєкторії
void dda_motion_planner_task(void *argument) {
    bool direction_state = true;
    bool last_direction = true;
    s_dda_worker_task_handle = xTaskGetCurrentTaskHandle();

    // Початкове заповнення обох половин буфера перед пуском
    dda_fill_buffer_section(&dda_gpio_dma_buffer[0], DDA_HALF_BUFFER_SIZE, direction_state, &last_direction);
    dda_fill_buffer_section(&dda_gpio_dma_buffer[DDA_HALF_BUFFER_SIZE], DDA_HALF_BUFFER_SIZE, direction_state, &last_direction);
    s_lower_half_busy = true;
    s_upper_half_busy = true;

    // Запуск потокового вивантаження DMA у кільцевому режимі
    HAL_DMA_Start_IT(&hdma_tim1_up, 
                     (uint32_t)dda_gpio_dma_buffer, 
                     (uint32_t)&(GPIOB->BSRR), 
                     DDA_FULL_BUFFER_SIZE);
    __HAL_TIM_ENABLE_DMA(&htim1, TIM_DMA_UPDATE);
    HAL_TIM_Base_Start(&htim1);

    for (;;) {
        // Очікування сповіщення від переривання DMA
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        if (!s_lower_half_busy) {
            dda_fill_buffer_section(&dda_gpio_dma_buffer[0], DDA_HALF_BUFFER_SIZE, direction_state, &last_direction);
            s_lower_half_busy = true;
        }

        if (!s_upper_half_busy) {
            dda_fill_buffer_section(&dda_gpio_dma_buffer[DDA_HALF_BUFFER_SIZE], DDA_HALF_BUFFER_SIZE, direction_state, &last_direction);
            s_upper_half_busy = true;
        }
    }
}
