#include <cstdint>
#include <array>
#include <algorithm>
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

template <std::size_t ChipCount>
class ShiftRegisterInputDMA {
public:
    using BufferType = std::array<uint8_t, ChipCount>;

    struct HardwareCallbacks {
        void (*triggerLatch)();
        bool (*startSpiDmaTransfer)(uint8_t* buffer, std::size_t length);
    };

    explicit ShiftRegisterInputDMA(const HardwareCallbacks& hw)
        : m_hw(hw), m_transferSemaphore(nullptr), m_dataMutex(nullptr) {
        m_rxShadowBuffer.fill(0);
        m_activeData.fill(0);
    }

    bool init() {
        m_transferSemaphore = xSemaphoreCreateBinary();
        m_dataMutex = xSemaphoreCreateMutex();
        return (m_transferSemaphore != nullptr) && (m_dataMutex != nullptr);
    }

    // Фонова процедура вибірки (викликається з періодичної RTOS-задачі)
    bool pollInputs(TickType_t maxWaitTicks = pdMS_TO_TICKS(10)) {
        // Фіксація сигналів апаратною лінією PL
        m_hw.triggerLatch();

        // Запуск передачі в теневий буфер
        if (!m_hw.startSpiDmaTransfer(m_rxShadowBuffer.data(), ChipCount)) {
            return false;
        }

        // Очікування завершення DMA-обміну через семафор
        if (xSemaphoreTake(m_transferSemaphore, maxWaitTicks) == pdTRUE) {
            processAndSwapBuffers();
            return true;
        }
        return false;
    }

    // Викликається з ISR після завершення прийому DMA
    void onTransferCompleteFromISR() {
        BaseType_t higherPriorityTaskWoken = pdFALSE;
        xSemaphoreGiveFromISR(m_transferSemaphore, &higherPriorityTaskWoken);
        portYIELD_FROM_ISR(higherPriorityTaskWoken);
    }

    // Потікобезпечне зчитування поточного стану всіх входів
    BufferType getSnapshot() const {
        BufferType snapshot{};
        if (xSemaphoreTake(m_dataMutex, portMAX_DELAY) == pdTRUE) {
            snapshot = m_activeData;
            xSemaphoreGive(m_dataMutex);
        }
        return snapshot;
    }

    // Перевірка стану конкретного біта (0 .. ChipCount*8 - 1)
    bool isBitSet(std::size_t bitIndex) const {
        if (bitIndex >= ChipCount * 8) return false;
        BufferType data = getSnapshot();
        std::size_t byteIdx = bitIndex / 8;
        std::size_t bitOffset = bitIndex % 8;
        return (data[byteIdx] & (1U << bitOffset)) != 0;
    }

private:
    HardwareCallbacks m_hw;
    SemaphoreHandle_t m_transferSemaphore;
    SemaphoreHandle_t m_dataMutex;
    BufferType m_rxShadowBuffer;
    BufferType m_activeData;

    void processAndSwapBuffers() {
        BufferType processed{};
        for (std::size_t i = 0; i < ChipCount; ++i) {
            std::size_t targetIndex = ChipCount - 1 - i;
            processed[targetIndex] = reverseBits(m_rxShadowBuffer[i]);
        }

        if (xSemaphoreTake(m_dataMutex, portMAX_DELAY) == pdTRUE) {
            m_activeData = processed;
            xSemaphoreGive(m_dataMutex);
        }
    }

    static uint8_t reverseBits(uint8_t b) {
        b = (b & 0xF0) >> 4 | (b & 0x0F) << 4;
        b = (b & 0xCC) >> 2 | (b & 0x33) << 2;
        b = (b & 0xAA) >> 1 | (b & 0x55) << 1;
        return b;
    }
};
