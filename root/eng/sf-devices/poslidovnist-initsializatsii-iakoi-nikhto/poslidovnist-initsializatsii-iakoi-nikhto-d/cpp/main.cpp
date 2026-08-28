#include <cstdint>
#include <concepts>
#include <expected>
#include <span>
#include <chrono>
#include "stm32f4xx.h"

namespace hal {

using namespace std::chrono_literals;

enum class InitError : uint8_t {
    Timeout,
    InvalidDeviceSignature,
    HardwareFault
};

class DwtTimer {
public:
    static void init() noexcept {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    }

    template <typename Rep, typename Period>
    static void delay(std::chrono::duration<Rep, Period> duration) noexcept {
        const auto micros = std::chrono::duration_cast<std::chrono::microseconds>(duration).count();
        const uint32_t ticks = static_cast<uint32_t>(micros) * (SystemCoreClock / 1'000'000U);
        const uint32_t start = DWT->CYCCNT;
        while ((DWT->CYCCNT - start) < ticks) {
            __NOP();
        }
    }
};

class SpiDmaMaster {
public:
    struct Config {
        std::chrono::microseconds reset_hold_time{15'000us};
        std::chrono::microseconds boot_settle_time{25'000us};
        uint32_t baudrate_prescaler{2U}; // F_PCLK / 8
    };

    explicit SpiDmaMaster(const Config& cfg) noexcept : config_(cfg) {}

    [[nodiscard]] std::expected<void, InitError> initialize(std::span<uint8_t> rx_buffer) noexcept {
        DwtTimer::init();

        // 1. Активація тактування підсистем
        enable_peripheral_clocks();

        // 2. Безпечна ініціалізація виводів без паразитних сплесків
        setup_gpio_pins();

        // 3. Фізичний цикл скидання зовнішнього пристрою
        perform_hardware_reset();

        // 4. Підготовка каналу DMA ДО активації SPI
        setup_dma_stream(rx_buffer);

        // 5. Конфігурація та активація інтерфейсу SPI
        setup_spi_registers();

        return {};
    }

private:
    Config config_;

    void enable_peripheral_clocks() noexcept {
        RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOCEN | RCC_AHB1ENR_DMA2EN;
        RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
        (void)RCC->APB2ENR; // Бар'єр шини APB
    }

    void setup_gpio_pins() noexcept {
        // nRST (PC4): активний низький -> притискаємо до LOW
        GPIOC->BSRR = GPIO_BSRR_BR4;
        GPIOC->MODER = (GPIOC->MODER & ~GPIO_MODER_MODER4_Msk) | (1U << GPIO_MODER_MODER4_Pos);

        // nCS (PA4): активний низький -> спочатку підтягуємо до HIGH!
        GPIOA->BSRR = GPIO_BSRR_BS4;
        GPIOA->MODER = (GPIOA->MODER & ~GPIO_MODER_MODER4_Msk) | (1U << GPIO_MODER_MODER4_Pos);

        // SCK (PA5), MISO (PA6), MOSI (PA7) -> Alternate Function AF5
        GPIOA->MODER &= ~(GPIO_MODER_MODER5_Msk | GPIO_MODER_MODER6_Msk | GPIO_MODER_MODER7_Msk);
        GPIOA->MODER |= (2U << GPIO_MODER_MODER5_Pos) | 
                        (2U << GPIO_MODER_MODER6_Pos) | 
                        (2U << GPIO_MODER_MODER7_Pos);
        GPIOA->AFR[0] |= (5U << GPIO_AFRL_AFSEL5_Pos) | 
                         (5U << GPIO_AFRL_AFSEL6_Pos) | 
                         (5U << GPIO_AFRL_AFSEL7_Pos);
    }

    void perform_hardware_reset() noexcept {
        DwtTimer::delay(config_.reset_hold_time);
        GPIOC->BSRR = GPIO_BSRR_BS4; // Зняття апаратного скидання
        DwtTimer::delay(config_.boot_settle_time);
    }

    void setup_dma_stream(std::span<uint8_t> buffer) noexcept {
        DMA2_Stream0->CR &= ~DMA_SxCR_EN;
        while (DMA2_Stream0->CR & DMA_SxCR_EN) {}

        DMA2->LIFCR = DMA_LIFCR_CTCIF0 | DMA_LIFCR_CTEIF0 | DMA_LIFCR_CDMEIF0 | DMA_LIFCR_CFEIF0;
        DMA2_Stream0->PAR = reinterpret_cast<uint32_t>(&(SPI1->DR));
        DMA2_Stream0->M0AR = reinterpret_cast<uint32_t>(buffer.data());
        DMA2_Stream0->NDTR = static_cast<uint32_t>(buffer.size());
        DMA2_Stream0->CR = (3U << DMA_SxCR_CHSEL_Pos) | DMA_SxCR_MINC | (1U << DMA_SxCR_PL_Pos) | DMA_SxCR_TCIE;

        NVIC_SetPriority(DMA2_Stream0_IRQn, 5);
        NVIC_ClearPendingIRQ(DMA2_Stream0_IRQn);
        NVIC_EnableIRQ(DMA2_Stream0_IRQn);

        DMA2_Stream0->CR |= DMA_SxCR_EN; // Запуск DMA до запуску SPI
    }

    void setup_spi_registers() noexcept {
        SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI | (config_.baudrate_prescaler << SPI_CR1_BR_Pos);
        (void)SPI1->SR;
        (void)SPI1->DR;

        SPI1->CR2 |= SPI_CR2_RXDMAEN;
        SPI1->CR1 |= SPI_CR1_SPE; // Активація SPI
    }
};

} // namespace hal
