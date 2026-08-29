/* Захоплення звуку через SAI у режимі I2S + DMA й задача обробки FreeRTOS.
 *
 * Тактування, виводи й переривання SAI лишаються там, де їх генерує CubeMX
 * (HAL_SAI_MspInit); тут — те, заради чого писався модуль: подвійний буфер,
 * сповіщення задачі з переривання й відновлення після зриву потоку.
 */
#include "main.h"           /* HAL сімейства STM32 + мітки виводів із CubeMX */

#include "FreeRTOS.h"
#include "task.h"

#include "acoustic_detector.h"

#define NOTIFY_HALF_DONE   (1u << 0)
#define NOTIFY_FULL_DONE   (1u << 1)
#define NOTIFY_STREAM_FAIL (1u << 2)

/* Скільки тримати тривожний вихід піднятим після впізнаної події. */
#define ALARM_HOLD_MS      2000u

/* Поріг певності, нижче якого подію вважаємо здогадом і мовчимо. */
#define ALARM_CONFIDENCE   0.75f

/* Подвійний буфер DMA: перша половина — кадр A, друга — кадр B.
 * Вирівнювання на 32 байти має дві причини одразу: інструкціям SMLAD і
 * бібліотеці CMSIS-NN потрібне слово, а інвалідація D-кешу на Cortex-M7
 * працює цілими рядками по 32 байти — невирівняний буфер вона зачепила б
 * разом із сусідніми змінними. */
static __attribute__((aligned(32))) int16_t dma_buffer[2 * AED_FRAME_SAMPLES];

static SAI_HandleTypeDef hsai_mic;
static DMA_HandleTypeDef hdma_mic_rx;
static TaskHandle_t audio_task_handle;
static aed_detector_t detector;

/* Мікрофон один, тому SAI ставимо в моно-режим: DMA пише рівно один
 * int16_t на відлік, і напівбуфер збігається з кадром обробки. Зі стерео
 * довелося б розплітати чергування каналів і тримати вдвічі більший буфер. */
static bool mic_capture_start(void)
{
    hdma_mic_rx.Instance                 = DMA1_Stream0;
    hdma_mic_rx.Init.Request             = DMA_REQUEST_SAI1_A;
    hdma_mic_rx.Init.Direction           = DMA_PERIPH_TO_MEMORY;
    hdma_mic_rx.Init.PeriphInc           = DMA_PINC_DISABLE;
    hdma_mic_rx.Init.MemInc              = DMA_MINC_ENABLE;
    hdma_mic_rx.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;
    hdma_mic_rx.Init.MemDataAlignment    = DMA_MDATAALIGN_HALFWORD;
    hdma_mic_rx.Init.Mode                = DMA_CIRCULAR;
    hdma_mic_rx.Init.Priority            = DMA_PRIORITY_HIGH;
    hdma_mic_rx.Init.FIFOMode            = DMA_FIFOMODE_DISABLE;

    if (HAL_DMA_Init(&hdma_mic_rx) != HAL_OK) {
        return false;
    }
    __HAL_LINKDMA(&hsai_mic, hdmarx, hdma_mic_rx);

    hsai_mic.Instance             = SAI1_Block_A;
    hsai_mic.Init.AudioMode       = SAI_MODEMASTER_RX;
    hsai_mic.Init.Synchro         = SAI_ASYNCHRONOUS;
    hsai_mic.Init.OutputDrive     = SAI_OUTPUTDRIVE_DISABLE;
    hsai_mic.Init.NoDivider       = SAI_MASTERDIVIDER_ENABLE;
    hsai_mic.Init.FIFOThreshold   = SAI_FIFOTHRESHOLD_HALF;
    hsai_mic.Init.AudioFrequency  = SAI_AUDIO_FREQUENCY_16K;
    hsai_mic.Init.MonoStereoMode  = SAI_MONOMODE;
    hsai_mic.Init.CompandingMode  = SAI_NOCOMPANDING;
    hsai_mic.Init.TriState        = SAI_OUTPUT_NOTRELEASED;

    if (HAL_SAI_InitProtocol(&hsai_mic, SAI_I2S_STANDARD,
                             SAI_PROTOCOL_DATASIZE_16BIT, 2) != HAL_OK) {
        return false;
    }

    /* Довжина рахується в елементах даних: обидві половини одразу,
     * бо DMA налаштовано на кільце. */
    return HAL_SAI_Receive_DMA(&hsai_mic, (uint8_t *)dma_buffer,
                               2u * AED_FRAME_SAMPLES) == HAL_OK;
}

void DMA1_Stream0_IRQHandler(void)
{
    HAL_DMA_IRQHandler(&hdma_mic_rx);
}

static void notify_from_isr(uint32_t bits)
{
    BaseType_t higher_woken = pdFALSE;

    if (audio_task_handle != NULL) {
        xTaskNotifyFromISR(audio_task_handle, bits, eSetBits, &higher_woken);
    }

    portYIELD_FROM_ISR(higher_woken);
}

/* Перша половина заповнена — DMA вже пише в другу. */
void HAL_SAI_RxHalfCpltCallback(SAI_HandleTypeDef *hsai)
{
    (void)hsai;
    notify_from_isr(NOTIFY_HALF_DONE);
}

void HAL_SAI_RxCpltCallback(SAI_HandleTypeDef *hsai)
{
    (void)hsai;
    notify_from_isr(NOTIFY_FULL_DONE);
}

/* Переповнення FIFO чи збій DMA: потік звуку розірвано. Мовчки продовжувати
 * не можна — у матриці ознак утворилася б склейка з двох різних моментів. */
void HAL_SAI_ErrorCallback(SAI_HandleTypeDef *hsai)
{
    (void)hsai;
    notify_from_isr(NOTIFY_STREAM_FAIL);
}

static void process_half(const int16_t *half)
{
#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
    /* На Cortex-M7 з увімкненим D-кешем ядро інакше прочитає власну
     * застарілу копію замість щойно записаних DMA відліків. */
    SCB_InvalidateDCache_by_Addr((uint32_t *)half, AED_FRAME_SAMPLES * sizeof(int16_t));
#endif
    aed_push_frame(&detector, half);
}

static void restart_stream(void)
{
    HAL_SAI_DMAStop(&hsai_mic);
    HAL_SAI_DeInit(&hsai_mic);

    aed_init(&detector);        /* фон доведеться калібрувати заново */

    while (!mic_capture_start()) {
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

void audio_processing_task(void *arg)
{
    (void)arg;

    audio_task_handle = xTaskGetCurrentTaskHandle();
    aed_init(&detector);

    if (!mic_capture_start()) {
        restart_stream();
    }

    TickType_t alarm_until = 0;
    unsigned silent_timeouts = 0;

    for (;;) {
        uint32_t flags = 0;

        /* Таймаут удвічі довший за напівбуфер: він і відпускає тривожний
         * вихід, і ловить зупинку SAI, яка не дала жодного переривання. */
        if (xTaskNotifyWait(0, UINT32_MAX, &flags, pdMS_TO_TICKS(50)) == pdFALSE) {
            if (++silent_timeouts >= 20u) {
                silent_timeouts = 0;
                restart_stream();
            }
        } else {
            silent_timeouts = 0;
        }

        if (flags & NOTIFY_STREAM_FAIL) {
            restart_stream();
            continue;
        }

        if (flags & NOTIFY_HALF_DONE) {
            process_half(&dma_buffer[0]);
        }
        if (flags & NOTIFY_FULL_DONE) {
            process_half(&dma_buffer[AED_FRAME_SAMPLES]);
        }

        aed_event_t event;
        float confidence;

        if (aed_poll(&detector, &event, &confidence) && confidence >= ALARM_CONFIDENCE) {
            HAL_GPIO_WritePin(ALARM_GPIO_Port, ALARM_Pin, GPIO_PIN_SET);
            alarm_until = xTaskGetTickCount() + pdMS_TO_TICKS(ALARM_HOLD_MS);
        }

        if (alarm_until != 0 && (int32_t)(xTaskGetTickCount() - alarm_until) >= 0) {
            HAL_GPIO_WritePin(ALARM_GPIO_Port, ALARM_Pin, GPIO_PIN_RESET);
            alarm_until = 0;
        }
    }
}
