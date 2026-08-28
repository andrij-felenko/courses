#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

/* Глобальні дескриптори */
SemaphoreHandle_t g_adc_ready_sem = NULL;

/* Обробник переривання завершення перетворення АЦП на C */
void ADC1_2_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    /* Перевірка апаратного прапорця End-Of-Conversion */
    if (ADC1->SR & ADC_SR_EOC) {
        ADC1->SR &= ~ADC_SR_EOC; /* Квитування переривання */

        /* Сигналізуємо задачі про готовність нових вимірювань */
        if (g_adc_ready_sem != NULL) {
            xSemaphoreGiveFromISR(g_adc_ready_sem, &xHigherPriorityTaskWoken);
        }
    }

    /* Відкладене перемикання контексту */
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

/* Задача нижньої половини (Bottom-Half) */
void adc_processing_task(void *pvParameters) {
    (void)pvParameters;
    for (;;) {
        /* Чекаємо сигналу від апаратного переривання */
        if (xSemaphoreTake(g_adc_ready_sem, portMAX_DELAY) == pdTRUE) {
            uint32_t raw_value = ADC1->DR;
            /* Повільна обробка: цифрова фільтрація, калібрування */
            // process_adc_sample(raw_value);
        }
    }
}
