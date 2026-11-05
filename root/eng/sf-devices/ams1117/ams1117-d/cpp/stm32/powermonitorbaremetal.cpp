#include "stm32f4xx.h"
#include <array>
#include <cstdint>
#include <atomic>

template <size_t BufferSize = 16, uint32_t EwmaShift = 3>
class PowerMonitorBareMetal {
public:
    static_assert((BufferSize % 2) == 0, "Buffer size must be even for dual-buffering");

    enum class PowerState : uint8_t {
        Ok       = 0x00,
        Warning  = 0x01,
        Critical = 0x02
    };

    static constexpr uint16_t ThresholdWarning = 3846U; // ~3.1 В
    static constexpr uint16_t ThresholdCritical = 3598U; // ~2.9 В

    PowerMonitorBareMetal() noexcept : m_filteredRaw(0), m_state(PowerState::Ok) {}

    void initHardwareRegisters() noexcept {
        RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_DMA2EN;
        RCC->APB1ENR |= RCC_APB1ENR_TIM3EN | RCC_APB1ENR_PWREN;
        RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;

        GPIOA->MODER |= (3U << (0 * 2));
        GPIOA->PUPDR &= ~(3U << (0 * 2));

        TIM3->PSC = (SystemCoreClock / 1000000U) - 1U;
        TIM3->ARR = 500U - 1U;
        TIM3->CR2 &= ~TIM_CR2_MMS;
        TIM3->CR2 |= (2U << TIM_CR2_MMS_Pos);

        DMA2_Stream0->CR &= ~DMA_SxCR_EN;
        while (DMA2_Stream0->CR & DMA_SxCR_EN);

        DMA2_Stream0->PAR = reinterpret_cast<uint32_t>(&(ADC1->DR));
        DMA2_Stream0->M0AR = reinterpret_cast<uint32_t>(m_dmaBuffer.data());
        DMA2_Stream0->NDTR = BufferSize;
        DMA2_Stream0->CR = (0U << DMA_SxCR_CHSEL_Pos) |
                           (1U << DMA_SxCR_PL_Pos)    |
                           (1U << DMA_SxCR_MSIZE_Pos) |
                           (1U << DMA_SxCR_PSIZE_Pos) |
                           DMA_SxCR_MINC              |
                           DMA_SxCR_CIRC              |
                           DMA_SxCR_HTIE              |
                           DMA_SxCR_TCIE;

        ADC1->CR1 = ADC_CR1_SCAN;
        ADC1->CR2 = ADC_CR2_DMA | ADC_CR2_DDS |
                    (1U << ADC_CR2_EXTEN_Pos) |
                    (8U << ADC_CR2_EXTSEL_Pos);
        ADC1->SQR1 = 0U;
        ADC1->SQR3 = 0U;
        ADC1->SMPR2 |= (4U << ADC_SMPR2_SMP0_Pos);

        NVIC_SetPriority(DMA2_Stream0_IRQn, 0);
        NVIC_EnableIRQ(DMA2_Stream0_IRQn);

        DMA2_Stream0->CR |= DMA_SxCR_EN;
        ADC1->CR2 |= ADC_CR2_ADON;
        TIM3->CR1 |= TIM_CR1_CEN;
    }

    void handleInterrupt() noexcept {
        if (DMA2->LISR & DMA_LISR_HTIF0) {
            DMA2->LIFCR = DMA_LIFCR_CHTIF0;
            processChunk(0, BufferSize / 2);
        }
        if (DMA2->LISR & DMA_LISR_TCIF0) {
            DMA2->LIFCR = DMA_LIFCR_CTCIF0;
            processChunk(BufferSize / 2, BufferSize / 2);
        }
    }

    [[nodiscard]] PowerState getState() const noexcept {
        return m_state.load(std::memory_order_relaxed);
    }

    [[nodiscard]] uint32_t getFilteredValue() const noexcept {
        return m_filteredRaw.load(std::memory_order_relaxed);
    }

private:
    void processChunk(size_t offset, size_t length) noexcept {
        uint32_t sum = 0;
        for (size_t i = offset; i < offset + length; ++i) {
            sum += m_dmaBuffer[i];
        }
        const uint32_t avg = sum / length;
        uint32_t currentFiltered = m_filteredRaw.load(std::memory_order_relaxed);

        if (currentFiltered == 0) {
            currentFiltered = avg;
        } else {
            currentFiltered = ((currentFiltered << EwmaShift) - currentFiltered + avg) >> EwmaShift;
        }
        m_filteredRaw.store(currentFiltered, std::memory_order_relaxed);

        if (currentFiltered < ThresholdCritical) {
            m_state.store(PowerState::Critical, std::memory_order_relaxed);
            FLASH->CR &= ~FLASH_CR_PG;
            PWR->CR |= PWR_CR_DBP;
            RTC->BKP0R = 0xDEADBEEFU;
        } else if (currentFiltered < ThresholdWarning) {
            m_state.store(PowerState::Warning, std::memory_order_relaxed);
        } else {
            m_state.store(PowerState::Ok, std::memory_order_relaxed);
        }
    }

    alignas(4) std::array<uint16_t, BufferSize> m_dmaBuffer{};
    std::atomic<uint32_t> m_filteredRaw;
    std::atomic<PowerState> m_state;
};
