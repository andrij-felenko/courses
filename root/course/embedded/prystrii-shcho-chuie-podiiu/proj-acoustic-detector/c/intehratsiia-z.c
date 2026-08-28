#include "FreeRTOS.h"
#include "task.h"
#include "acoustic_detector.h"

#define EVENT_BIT_DMA_HALF_TRANSFER  (1 << 0)
#define EVENT_BIT_DMA_FULL_TRANSFER  (1 << 1)

static TaskHandle_t audio_task_handle = NULL;
static detector_context_t detector_ctx;
static int16_t dma_double_buffer[AUDIO_FRAME_SAMPLES * 2];

void DMA1_Stream0_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    // Перевірка Half-Transfer прапорця
    if (DMA1->LISR & DMA_LISR_HTIF0) {
        DMA1->LIFCR = DMA_LIFCR_CHTIF0;
        xTaskNotifyFromISR(audio_task_handle, EVENT_BIT_DMA_HALF_TRANSFER,
                           eSetBits, &xHigherPriorityTaskWoken);
    }
    // Перевірка Transfer-Complete прапорця
    if (DMA1->LISR & DMA_LISR_TCIF0) {
        DMA1->LIFCR = DMA_LIFCR_CTCIF0;
        xTaskNotifyFromISR(audio_task_handle, EVENT_BIT_DMA_FULL_TRANSFER,
                           eSetBits, &xHigherPriorityTaskWoken);
    }

    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

void audio_processing_task(void *pvParameters) {
    (void)pvParameters;
    detector_init(&detector_ctx);

    uint32_t notified_events = 0;
    for (;;) {
        // Очікування події від DMA без навантаження на процесор
        xTaskNotifyWait(0x00, 0xFFFFFFFF, &notified_events, portMAX_DELAY);

        if (notified_events & EVENT_BIT_DMA_HALF_TRANSFER) {
            detector_process_half_buffer(&detector_ctx, &dma_double_buffer[0], AUDIO_FRAME_SAMPLES);
        }
        if (notified_events & EVENT_BIT_DMA_FULL_TRANSFER) {
            detector_process_half_buffer(&detector_ctx, &dma_double_buffer[AUDIO_FRAME_SAMPLES], AUDIO_FRAME_SAMPLES);
        }

        acoustic_event_t event;
        float confidence;
        if (detector_poll_event(&detector_ctx, &event, &confidence)) {
            if (confidence > 0.75f) {
                // Активація радіопередавача LoRa або звукової сигналізації
            }
        }
    }
}
