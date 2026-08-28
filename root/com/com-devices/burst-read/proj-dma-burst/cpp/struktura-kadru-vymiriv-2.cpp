#include "stm32f4xx_hal.h"
#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <numbers>
#include <span>

namespace sensor {

struct MotionSample {
    std::array<float, 3> accel{};
    std::array<float, 3> gyro{};
    float temperature_c{};
};

class ImuDmaDriver {
public:
    static constexpr size_t kFrameSize = 15;
    static constexpr uint8_t kBurstCmd = 0x80 | 0x20;

    explicit ImuDmaDriver(SPI_HandleTypeDef& spi, GPIO_TypeDef* cs_port, uint16_t cs_pin) noexcept
        : spi_(spi), cs_port_(cs_port), cs_pin_(cs_pin) {
        tx_buf_.fill(0x00);
        tx_buf_[0] = kBurstCmd;
    }

    void start_burst_transfer() noexcept {
        HAL_GPIO_WritePin(cs_port_, cs_pin_, GPIO_PIN_RESET);
        const uint8_t idx = active_buf_idx_.load(std::memory_order_relaxed);
        HAL_SPI_TransmitReceive_DMA(&spi_, tx_buf_.data(), rx_double_buf_[idx].data(), kFrameSize);
    }

    void on_dma_complete_isr() noexcept {
        HAL_GPIO_WritePin(cs_port_, cs_pin_, GPIO_PIN_SET);
        active_buf_idx_.store(active_buf_idx_.load(std::memory_order_relaxed) ^ 1, std::memory_order_release);
        has_new_data_.store(true, std::memory_order_release);
    }

private:
    SPI_HandleTypeDef& spi_;
    GPIO_TypeDef*      cs_port_;
    uint16_t           cs_pin_;
    alignas(4) std::array<uint8_t, kFrameSize> tx_buf_{};
    alignas(4) std::array<std::array<uint8_t, kFrameSize>, 2> rx_double_buf_{};
    std::atomic<uint8_t> active_buf_idx_{0};
    std::atomic<bool>    has_new_data_{false};
};

} // namespace sensor
