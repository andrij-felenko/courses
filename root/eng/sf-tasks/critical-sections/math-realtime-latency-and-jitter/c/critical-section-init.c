#include <stdint.h>
#include "stm32f4xx.h"
#include "FreeRTOS.h"
#include "semphr.h"

static SemaphoreHandle_t xMutex = NULL;

void critical_section_init(void) {
    // Створення м'ютексу з підтримкою успадкування пріоритетів
    xMutex = xSemaphoreCreateMutex();
}

uint32_t execute_critical_section(volatile uint32_t *hardware_register, uint32_t value) {
    uint32_t elapsed_cycles = 0;
    
    if (xMutex != NULL && xSemaphoreTake(xMutex, portMAX_DELAY) == pdTRUE) {
        uint32_t start_cycles = DWT->CYCCNT; // Зчитування лічильника тактів ядра
        
        // Вхід у критичну секцію із маскуванням переривань
        taskENTER_CRITICAL();
        
        *hardware_register += value;
        __DSB(); // Бар'єр синхронізації даних
        
        taskEXIT_CRITICAL(); // Вихід із критичної секції
        
        elapsed_cycles = DWT->CYCCNT - start_cycles;
        xSemaphoreGive(xMutex);
    }
    
    return elapsed_cycles;
}
