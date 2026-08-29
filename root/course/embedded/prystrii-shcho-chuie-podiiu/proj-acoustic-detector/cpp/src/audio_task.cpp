// Захоплення звуку через SAI у режимі I2S + DMA й задача обробки FreeRTOS.
//
// Тактування, виводи й переривання SAI лишаються там, де їх генерує CubeMX
// (HAL_SAI_MspInit); тут — те, заради чого писався модуль: подвійний буфер,
// сповіщення задачі з переривання й відновлення після зриву потоку.
#include <array>
#include <cstdint>
#include <span>

#include "main.h"        // HAL сімейства STM32 + мітки виводів із CubeMX

#include "FreeRTOS.h"
#include "task.h"

#include "acoustic/detector.hpp"

namespace {

using namespace acoustic;

constexpr std::uint32_t kNotifyHalfDone   = 1u << 0;
constexpr std::uint32_t kNotifyFullDone   = 1u << 1;
constexpr std::uint32_t kNotifyStreamFail = 1u << 2;

// Скільки тримати тривожний вихід піднятим після впізнаної події.
constexpr std::uint32_t kAlarmHoldMs = 2000;

// Поріг певності, нижче якого подію вважаємо здогадом і мовчимо.
constexpr float kAlarmConfidence = 0.75f;

// Подвійний буфер DMA: перша половина — кадр A, друга — кадр B.
// Вирівнювання на 32 байти має дві причини одразу: інструкціям SMLAD і
// бібліотеці CMSIS-NN потрібне слово, а інвалідація D-кешу на Cortex-M7
// працює цілими рядками по 32 байти — невирівняний буфер вона зачепила б
// разом із сусідніми змінними.
alignas(32) std::array<std::int16_t, 2 * kFrameSamples> dmaBuffer{};

SAI_HandleTypeDef  sai{};
DMA_HandleTypeDef  saiDma{};
TaskHandle_t       audioTask = nullptr;
Detector           detector{};

// Мікрофон один, тому SAI ставимо в моно-режим: DMA пише рівно один int16_t
// на відлік, і напівбуфер збігається з кадром обробки. Зі стерео довелося б
// розплітати чергування каналів і тримати вдвічі більший буфер.
bool startCapture() noexcept
{
    saiDma.Instance                 = DMA1_Stream0;
    saiDma.Init.Request             = DMA_REQUEST_SAI1_A;
    saiDma.Init.Direction           = DMA_PERIPH_TO_MEMORY;
    saiDma.Init.PeriphInc           = DMA_PINC_DISABLE;
    saiDma.Init.MemInc              = DMA_MINC_ENABLE;
    saiDma.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;
    saiDma.Init.MemDataAlignment    = DMA_MDATAALIGN_HALFWORD;
    saiDma.Init.Mode                = DMA_CIRCULAR;
    saiDma.Init.Priority            = DMA_PRIORITY_HIGH;
    saiDma.Init.FIFOMode            = DMA_FIFOMODE_DISABLE;

    if (HAL_DMA_Init(&saiDma) != HAL_OK) {
        return false;
    }
    __HAL_LINKDMA(&sai, hdmarx, saiDma);

    sai.Instance            = SAI1_Block_A;
    sai.Init.AudioMode      = SAI_MODEMASTER_RX;
    sai.Init.Synchro        = SAI_ASYNCHRONOUS;
    sai.Init.OutputDrive    = SAI_OUTPUTDRIVE_DISABLE;
    sai.Init.NoDivider      = SAI_MASTERDIVIDER_ENABLE;
    sai.Init.FIFOThreshold  = SAI_FIFOTHRESHOLD_HALF;
    sai.Init.AudioFrequency = SAI_AUDIO_FREQUENCY_16K;
    sai.Init.MonoStereoMode = SAI_MONOMODE;
    sai.Init.CompandingMode = SAI_NOCOMPANDING;
    sai.Init.TriState       = SAI_OUTPUT_NOTRELEASED;

    if (HAL_SAI_InitProtocol(&sai, SAI_I2S_STANDARD,
                             SAI_PROTOCOL_DATASIZE_16BIT, 2) != HAL_OK) {
        return false;
    }

    // Довжина рахується в елементах даних: обидві половини одразу, бо DMA
    // налаштовано на кільце.
    return HAL_SAI_Receive_DMA(&sai, reinterpret_cast<std::uint8_t *>(dmaBuffer.data()),
                               dmaBuffer.size()) == HAL_OK;
}

void notifyFromIsr(std::uint32_t bits) noexcept
{
    BaseType_t higherWoken = pdFALSE;

    if (audioTask != nullptr) {
        xTaskNotifyFromISR(audioTask, bits, eSetBits, &higherWoken);
    }
    portYIELD_FROM_ISR(higherWoken);
}

void processHalf(std::span<const std::int16_t, kFrameSamples> half) noexcept
{
#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
    // На Cortex-M7 з увімкненим D-кешем ядро інакше прочитає власну застарілу
    // копію замість щойно записаних DMA відліків.
    SCB_InvalidateDCache_by_Addr(
        reinterpret_cast<std::uint32_t *>(const_cast<std::int16_t *>(half.data())),
        static_cast<std::int32_t>(half.size_bytes()));
#endif
    detector.push(half);
}

void restartStream() noexcept
{
    HAL_SAI_DMAStop(&sai);
    HAL_SAI_DeInit(&sai);

    detector.reset();   // фон доведеться калібрувати заново

    while (!startCapture()) {
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

// Тривожний вихід із утриманням: піднявся на подію, сам опустився через
// дві секунди. Стан живе в одному місці, тож забути опустити пін ніде.
class AlarmOutput {
public:
    void raise() noexcept
    {
        HAL_GPIO_WritePin(ALARM_GPIO_Port, ALARM_Pin, GPIO_PIN_SET);
        holdUntil_ = xTaskGetTickCount() + pdMS_TO_TICKS(kAlarmHoldMs);
        held_ = true;
    }

    void tick() noexcept
    {
        if (held_ && static_cast<std::int32_t>(xTaskGetTickCount() - holdUntil_) >= 0) {
            HAL_GPIO_WritePin(ALARM_GPIO_Port, ALARM_Pin, GPIO_PIN_RESET);
            held_ = false;
        }
    }

private:
    TickType_t holdUntil_{0};
    bool       held_{false};
};

}  // namespace

// HAL і вектори переривань — код мовою C, тож зв'язування теж має бути C.
extern "C" {

void DMA1_Stream0_IRQHandler()
{
    HAL_DMA_IRQHandler(&saiDma);
}

// Перша половина заповнена — DMA вже пише в другу.
void HAL_SAI_RxHalfCpltCallback(SAI_HandleTypeDef *)
{
    notifyFromIsr(kNotifyHalfDone);
}

void HAL_SAI_RxCpltCallback(SAI_HandleTypeDef *)
{
    notifyFromIsr(kNotifyFullDone);
}

// Переповнення FIFO чи збій DMA: потік звуку розірвано. Мовчки продовжувати
// не можна — у матриці ознак утворилася б склейка з двох різних моментів.
void HAL_SAI_ErrorCallback(SAI_HandleTypeDef *)
{
    notifyFromIsr(kNotifyStreamFail);
}

void audioProcessingTask(void *)
{
    audioTask = xTaskGetCurrentTaskHandle();
    detector.reset();

    if (!startCapture()) {
        restartStream();
    }

    const std::span buffer{dmaBuffer};
    const auto firstHalf  = buffer.first<kFrameSamples>();
    const auto secondHalf = buffer.last<kFrameSamples>();

    AlarmOutput alarm{};
    unsigned silentTimeouts = 0;

    for (;;) {
        std::uint32_t flags = 0;

        // Таймаут удвічі довший за напівбуфер: він і відпускає тривожний
        // вихід, і ловить зупинку SAI, яка не дала жодного переривання.
        if (xTaskNotifyWait(0, UINT32_MAX, &flags, pdMS_TO_TICKS(50)) == pdFALSE) {
            if (++silentTimeouts >= 20) {
                silentTimeouts = 0;
                restartStream();
            }
        } else {
            silentTimeouts = 0;
        }

        if ((flags & kNotifyStreamFail) != 0) {
            restartStream();
            continue;
        }

        if ((flags & kNotifyHalfDone) != 0) {
            processHalf(firstHalf);
        }
        if ((flags & kNotifyFullDone) != 0) {
            processHalf(secondHalf);
        }

        if (const auto detection = detector.poll();
            detection && detection->confidence >= kAlarmConfidence) {
            alarm.raise();
        }
        alarm.tick();
    }
}

}  // extern "C"
