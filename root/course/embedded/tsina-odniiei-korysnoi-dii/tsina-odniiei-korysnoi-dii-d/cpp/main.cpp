// ============================================================================
// C++20 / RAII Scoped Power Management & Hardware Safety
// ============================================================================
#include <cstdint>
#include <span>
#include "stm32l4xx_ll_gpio.h"
#include "stm32l4xx_ll_pwr.h"
#include "stm32l4xx_ll_adc.h"
#include "stm32l4xx_ll_dma.h"

namespace power_opt {

// ── RAII-керування живленням зовнішнього сенсора ────────────────────────────
class ScopedSensorPower {
public:
    inline ScopedSensorPower(GPIO_TypeDef* port, uint32_t pin) noexcept 
        : port_(port), pin_(pin) 
    {
        LL_GPIO_ResetOutputPin(port_, pin_); // Увімкнути P-MOSFET ключ
    }

    inline ~ScopedSensorPower() noexcept {
        LL_GPIO_SetOutputPin(port_, pin_);   // Знеструмити сенсор
    }

    ScopedSensorPower(const ScopedSensorPower&) = delete;
    ScopedSensorPower& operator=(const ScopedSensorPower&) = delete;

private:
    GPIO_TypeDef* port_;
    uint32_t pin_;
};

// ── Клас захисту невикористовуваних пінів від витоків Crowbar ───────────────
class PinLeakageGuard {
public:
    static void isolate_unused_gpio() noexcept {
        // Переведення порту B в аналоговий режим (усі піни в High-Z)
        GPIOB->MODER = 0xFFFFFFFF;
        GPIOB->PUPDR = 0x00000000;
    }
};

// ── Автономний збирач даних з переходом у сон ───────────────────────────────
class AutonomousDataAcquisition {
public:
    explicit AutonomousDataAcquisition(ADC_TypeDef* adc, DMA_TypeDef* dma, uint32_t channel) noexcept
        : adc_(adc), dma_(dma), channel_(channel) {}

    void acquire_samples(std::span<uint32_t> output_buffer, GPIO_TypeDef* pwr_port, uint32_t pwr_pin) noexcept {
        ScopedSensorPower power_guard(pwr_port, pwr_pin);

        // Просте апаратне очікування стабілізації
        for (volatile int i = 0; i < 500; ++i) {}

        LL_DMA_ConfigAddresses(dma_, channel_,
                               LL_ADC_DMA_GetRegAddr(adc_, LL_ADC_DMA_REG_REGULAR_DATA),
                               reinterpret_cast<uint32_t>(output_buffer.data()),
                               LL_DMA_DIRECTION_PERIPH_TO_MEMORY);
        LL_DMA_SetDataLength(dma_, channel_, static_cast<uint32_t>(output_buffer.size()));
        LL_DMA_EnableIT_TC(dma_, channel_);
        LL_DMA_EnableChannel(dma_, channel_);

        LL_ADC_REG_StartConversion(adc_);

        // Засинання ядра: робота периферії без участі CPU
        __WFI();

        LL_DMA_DisableChannel(dma_, channel_);
    }

private:
    ADC_TypeDef* adc_;
    DMA_TypeDef* dma_;
    uint32_t channel_;
};

} // namespace power_opt
