// ============================================================================
// C++20 / RAII Scoped Profiler & Hardware Abstraction
// ============================================================================
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include "stm32l4xx.h"
#include "stm32l4xx_ll_rcc.h"
#include "stm32l4xx_ll_adc.h"
#include "stm32l4xx_ll_i2c.h"

namespace energy_profiler {

// ── RAII-обгортка апаратного GPIO маркера ────────────────────────────────────
template <uint32_t PinSetMask, uint32_t PinClrMask>
class ScopedGpioMarker {
public:
    inline ScopedGpioMarker() noexcept {
        GPIOA->BSRR = PinSetMask;
    }
    inline ~ScopedGpioMarker() noexcept {
        GPIOA->BSRR = PinClrMask;
    }
    ScopedGpioMarker(const ScopedGpioMarker&) = delete;
    ScopedGpioMarker& operator=(const ScopedGpioMarker&) = delete;
};

using PhaseMarker = ScopedGpioMarker<GPIO_BSRR_BS0, GPIO_BSRR_BR0>;
using SubMarker   = ScopedGpioMarker<GPIO_BSRR_BS1, GPIO_BSRR_BR1>;

// ── Клас апаратного лічильника тактів DWT ───────────────────────────────────
class CycleCounter {
public:
    static void init() noexcept {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
        DWT->CYCCNT = 0;
    }

    [[nodiscard]] static inline uint32_t get() noexcept {
        return DWT->CYCCNT;
    }
};

struct BenchmarkMetrics {
    uint32_t pll_lock_cycles{0};
    uint32_t adc_sample_cycles{0};
    uint32_t i2c_poll_cycles{0};
    uint32_t crc_calc_cycles{0};
};

enum class BusError {
    Timeout,
    Nack,
    BusBusy
};

// ── Автономний клас вимірювань ──────────────────────────────────────────────
class MicroBenchmark {
public:
    explicit MicroBenchmark(BenchmarkMetrics& metrics) noexcept 
        : metrics_(metrics) {}

    void measure_pll_startup() noexcept {
        PhaseMarker marker;
        const uint32_t start = CycleCounter::get();

        LL_RCC_PLL_Enable();
        while (!LL_RCC_PLL_IsReady()) {
            // Очікування синхронізації
        }
        LL_RCC_SetSysClkSource(LL_RCC_SYS_CLKSOURCE_PLL);
        while (LL_RCC_GetSysClkSource() != LL_RCC_SYS_CLKSOURCE_STATUS_PLL) {
            // Очікування готовності
        }

        metrics_.pll_lock_cycles = CycleCounter::get() - start;
    }

    [[nodiscard]] std::expected<uint16_t, BusError> measure_adc_sample() noexcept {
        PhaseMarker marker;
        const uint32_t start = CycleCounter::get();

        LL_ADC_EnableInternalRegulator(ADC1);
        for (volatile int i = 0; i < 1000; ++i) { /* Стабілізація VREF */ }

        LL_ADC_StartCalibration(ADC1, LL_ADC_SINGLE_ENDED);
        while (LL_ADC_IsCalibrationOnGoing(ADC1)) {}

        LL_ADC_Enable(ADC1);
        while (!LL_ADC_IsReady(ADC1)) {}

        uint16_t val = 0;
        {
            SubMarker sub_marker;
            LL_ADC_REG_StartConversion(ADC1);
            while (!LL_ADC_IsActiveFlag_EOC(ADC1)) {}
            val = LL_ADC_REG_ReadConversionData12(ADC1);
        }

        metrics_.adc_sample_cycles = CycleCounter::get() - start;
        return val;
    }

    [[nodiscard]] std::expected<void, BusError> measure_i2c_read(
        uint8_t dev_addr, uint8_t reg_addr, std::span<uint8_t> rx_buffer) noexcept 
    {
        PhaseMarker marker;
        const uint32_t start = CycleCounter::get();

        LL_I2C_HandleTransfer(I2C1, dev_addr, LL_I2C_ADDRSLAVE_7BIT, 1, 
                              LL_I2C_MODE_SOFTEND, LL_I2C_GENERATE_START_WRITE);
        while (!LL_I2C_IsActiveFlag_TXIS(I2C1)) {}
        LL_I2C_TransmitData8(I2C1, reg_addr);
        while (!LL_I2C_IsActiveFlag_TC(I2C1)) {}

        LL_I2C_HandleTransfer(I2C1, dev_addr, LL_I2C_ADDRSLAVE_7BIT, 
                              static_cast<uint32_t>(rx_buffer.size()), 
                              LL_I2C_MODE_AUTOEND, LL_I2C_GENERATE_START_READ);

        for (auto& byte : rx_buffer) {
            while (!LL_I2C_IsActiveFlag_RXNE(I2C1)) {}
            byte = LL_I2C_ReceiveData8(I2C1);
        }
        while (!LL_I2C_IsActiveFlag_STOP(I2C1)) {}
        LL_I2C_ClearFlag_STOP(I2C1);

        metrics_.i2c_poll_cycles = CycleCounter::get() - start;
        return {};
    }

    [[nodiscard]] uint16_t measure_crc16(std::span<const uint8_t> payload) noexcept {
        PhaseMarker marker;
        const uint32_t start = CycleCounter::get();

        uint16_t crc = 0xFFFF;
        for (const uint8_t b : payload) {
            crc ^= static_cast<uint16_t>(b) << 8;
            for (int bit = 0; bit < 8; ++bit) {
                crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
            }
        }

        metrics_.crc_calc_cycles = CycleCounter::get() - start;
        return crc;
    }

private:
    BenchmarkMetrics& metrics_;
};

} // namespace energy_profiler
