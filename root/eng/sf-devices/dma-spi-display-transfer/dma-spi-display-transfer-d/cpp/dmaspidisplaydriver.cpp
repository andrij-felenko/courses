#include <cstdint>
#include <functional>

/* Клас асинхронного драйвера SPI-дисплея з DMA-прискоренням */
class DmaSpiDisplayDriver {
public:
    using CompletionCallback = std::function<void()>;

    DmaSpiDisplayDriver(uint16_t* bufA, uint16_t* bufB, uint32_t pixelCount)
        : m_bufferA(bufA), m_bufferB(bufB), m_pixelCount(pixelCount), m_isBusy(false) {}

    bool sendBufferAsync(const uint16_t* buffer, CompletionCallback callback) {
        if (m_isBusy) {
            return false;
        }

        m_onComplete = callback;
        m_isBusy = true;

        setPinDataMode(true);
        setChipSelect(true);

        flushDataCache(buffer, m_pixelCount * sizeof(uint16_t));
        setupAndStartDmaHardware(buffer, m_pixelCount * sizeof(uint16_t));

        return true;
    }

    void handleInterrupt() {
        clearInterruptFlag();
        waitUntilSpiTxFinished();
        setChipSelect(false);

        m_isBusy = false;

        if (m_onComplete) {
            m_onComplete();
        }
    }

    bool isBusy() const { return m_isBusy; }

private:
    uint16_t* m_bufferA;
    uint16_t* m_bufferB;
    uint32_t m_pixelCount;
    volatile bool m_isBusy;
    CompletionCallback m_onComplete;

    void setPinDataMode(bool isData) {
        /* Низькорівневе перемикання лінії D/C */
    }

    void setChipSelect(bool active) {
        /* Низькорівневе перемикання CS */
    }

    void flushDataCache(const void* addr, uint32_t size) {
        /* Скидання кешу даних L1 */
    }

    void setupAndStartDmaHardware(const void* src, uint32_t length) {
        /* Ініціалізація та запуск каналу DMA Engine */
    }

    void clearInterruptFlag() {
        /* Очищення регістру переривань DMA */
    }

    void waitUntilSpiTxFinished() {
        /* Перевірка прапорця BSY периферичного контролера SPI */
    }
};
