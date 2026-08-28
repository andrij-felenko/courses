#include <cstdint>
#include <span>
#include <concepts>
#include "stm32f4xx_ll_spi.h"
#include "stm32f4xx_ll_dma.h"
#include "stm32f4xx_ll_gpio.h"

// Концепт для апаратної конфігурації лінії CS
struct GpioPin {
    GPIO_TypeDef* port;
    uint32_t pin;
};

// RAII-клас керування транзакцією SPI з прецизійним контролем таймінгу CS
class SpiDmaSession {
public:
    // Конструктор: захоплює лінію CS та витримує інтервал t_CSS
    explicit SpiDmaSession(SPI_TypeDef* spi, GpioPin cs) noexcept
        : spi_(spi), cs_(cs), active_(true) {
        LL_GPIO_ResetOutputPin(cs_.port, cs_.pin);
        guard_delay(); // Забезпечуємо t_CSS перед першим тактовим імпульсом
    }

    // Заборона копіювання для запобігання подвійному підйому CS
    SpiDmaSession(const SpiDmaSession&) = delete;
    SpiDmaSession& operator=(const SpiDmaSession&) = delete;

    // Підтримка семантики переміщення
    SpiDmaSession(SpiDmaSession&& other) noexcept
        : spi_(other.spi_), cs_(other.cs_), active_(other.active_) {
        other.active_ = false;
    }

    SpiDmaSession& operator=(SpiDmaSession&& other) noexcept {
        if (this != &other) {
            if (active_) {
                finalize();
            }
            spi_ = other.spi_;
            cs_ = other.cs_;
            active_ = other.active_;
            other.active_ = false;
        }
        return *this;
    }

    // Передача блоку даних із використанням std::span
    [[nodiscard]] bool transmit(DMA_TypeDef* dma, uint32_t stream,
                                std::span<const uint8_t> data) noexcept {
        if (!active_ || data.empty()) {
            return false;
        }

        LL_DMA_DisableStream(dma, stream);
        LL_DMA_SetMemoryAddress(dma, stream, reinterpret_cast<uint32_t>(data.data()));
        LL_DMA_SetDataLength(dma, stream, static_cast<uint32_t>(data.size()));
        LL_DMA_ClearFlag_TC4(dma);
        LL_DMA_ClearFlag_TE4(dma);

        LL_SPI_EnableDMAReq_TX(spi_);
        LL_DMA_EnableStream(dma, stream);
        LL_SPI_Enable(spi_);

        // Очікування спустошення пам'яті контролером DMA
        while (!LL_DMA_IsActiveFlag_TC4(dma)) {
            if (LL_DMA_IsActiveFlag_TE4(dma)) {
                LL_DMA_DisableStream(dma, stream);
                LL_SPI_DisableDMAReq_TX(spi_);
                return false;
            }
        }

        LL_DMA_DisableStream(dma, stream);
        LL_SPI_DisableDMAReq_TX(spi_);
        return true;
    }

    // Деструктор: автоматично та безпечно деактивує CS при виході з області видимості
    ~SpiDmaSession() noexcept {
        if (active_) {
            finalize();
        }
    }

private:
    void finalize() noexcept {
        // 1. Очікуємо звільнення буфера даних
        while (!LL_SPI_IsActiveFlag_TXE(spi_)) {
        }

        // 2. Очікуємо закінчення фізичного тактування SCLK у зсувному регістрі
        while (LL_SPI_IsActiveFlag_BSY(spi_)) {
        }

        // 3. Витримуємо t_CSH
        guard_delay();

        // 4. Піднімаємо CS
        LL_GPIO_SetOutputPin(cs_.port, cs_.pin);

        // 5. Витримуємо паузу відновлення t_CS_HIGH
        guard_delay();
        active_ = false;
    }

    static void guard_delay() noexcept {
        __NOP(); __NOP(); __NOP(); __NOP();
        __NOP(); __NOP(); __NOP(); __NOP();
    }

    SPI_TypeDef* spi_{nullptr};
    GpioPin cs_{nullptr, 0};
    bool active_{false};
};
