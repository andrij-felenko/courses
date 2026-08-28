#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include "stm32l4xx_hal.h"

enum class DriverError {
    BusError,
    Timeout,
    FifoNotReady,
    DmaError
};

struct SensorSample {
    int16_t x{0};
    int16_t y{0};
    int16_t z{0};
};

template <size_t WatermarkSize = 32>
class FifoSensorDriver {
public:
    static constexpr size_t FrameSize = 6;
    static constexpr size_t BurstSize = WatermarkSize * FrameSize;

    FifoSensorDriver(SPI_HandleTypeDef& hspi, GPIO_TypeDef* cs_port, uint16_t cs_pin)
        : m_hspi(hspi), m_cs_port(cs_port), m_cs_pin(cs_pin) {
        m_tx_cmd_buffer.fill(0x00);
        m_tx_cmd_buffer[0] = RegFifoDataOut | SpiReadBit | SpiAutoIncrBit;
    }

    std::expected<void, DriverError> init() {
        /* Режим FIFO Stream + поріг 32 зразки */
        if (!writeRegister(RegFifoCtrl, 0x5F)) return std::unexpected(DriverError::BusError);
        /* Переривання Watermark на пін INT1 */
        if (!writeRegister(RegInt1Ctrl, 0x08)) return std::unexpected(DriverError::BusError);
        /* Запуск перетворень: 100 Гц ODR */
        if (!writeRegister(RegCtrlReg1, 0x57)) return std::unexpected(DriverError::BusError);

        m_data_ready = false;
        return {};
    }

    void onInterrupt() noexcept {
        m_data_ready = true;
    }

    std::expected<void, DriverError> startBurstReadDma() {
        if (!m_data_ready) {
            return std::unexpected(DriverError::FifoNotReady);
        }

        auto status = readRegister(RegFifoSrc);
        if (!status.has_value() || !(status.value() & 0x80)) {
            m_data_ready = false;
            return std::unexpected(DriverError::FifoNotReady);
        }

        setCs(false);
        HAL_StatusTypeDef hal_stat = HAL_SPI_TransmitReceive_DMA(
            &m_hspi,
            m_tx_cmd_buffer.data(),
            m_rx_raw_buffer.data(),
            static_cast<uint16_t>(m_rx_raw_buffer.size())
        );

        if (hal_stat != HAL_OK) {
            setCs(true);
            return std::unexpected(DriverError::DmaError);
        }

        return {};
    }

    void onDmaComplete() noexcept {
        setCs(true);
        m_data_ready = false;

        const uint8_t* raw = &m_rx_raw_buffer[1];
        for (size_t i = 0; i < WatermarkSize; ++i) {
            size_t offset = i * FrameSize;
            m_samples[i].x = static_cast<int16_t>(static_cast<uint16_t>(raw[offset + 0]) | 
                                                  (static_cast<uint16_t>(raw[offset + 1]) << 8));
            m_samples[i].y = static_cast<int16_t>(static_cast<uint16_t>(raw[offset + 2]) | 
                                                  (static_cast<uint16_t>(raw[offset + 3]) << 8));
            m_samples[i].z = static_cast<int16_t>(static_cast<uint16_t>(raw[offset + 4]) | 
                                                  (static_cast<uint16_t>(raw[offset + 5]) << 8));
        }
    }

    [[nodiscard]] std::span<const SensorSample, WatermarkSize> samples() const noexcept {
        return m_samples;
    }

private:
    static constexpr uint8_t RegCtrlReg1     = 0x20;
    static constexpr uint8_t RegInt1Ctrl     = 0x22;
    static constexpr uint8_t RegFifoDataOut  = 0x28;
    static constexpr uint8_t RegFifoCtrl     = 0x2E;
    static constexpr uint8_t RegFifoSrc      = 0x2F;

    static constexpr uint8_t SpiReadBit      = 0x80;
    static constexpr uint8_t SpiAutoIncrBit  = 0x40;

    void setCs(bool level) const noexcept {
        HAL_GPIO_WritePin(m_cs_port, m_cs_pin, level ? GPIO_PIN_SET : GPIO_PIN_RESET);
    }

    bool writeRegister(uint8_t reg, uint8_t val) const noexcept {
        uint8_t tx[2] = { static_cast<uint8_t>(reg & ~SpiReadBit), val };
        setCs(false);
        bool ok = (HAL_SPI_Transmit(&m_hspi, tx, 2, HAL_MAX_DELAY) == HAL_OK);
        setCs(true);
        return ok;
    }

    std::expected<uint8_t, DriverError> readRegister(uint8_t reg) const noexcept {
        uint8_t tx[2] = { static_cast<uint8_t>(reg | SpiReadBit), 0x00 };
        uint8_t rx[2] = { 0 };
        setCs(false);
        HAL_StatusTypeDef status = HAL_SPI_TransmitReceive(&m_hspi, tx, rx, 2, HAL_MAX_DELAY);
        setCs(true);
        if (status != HAL_OK) return std::unexpected(DriverError::BusError);
        return rx[1];
    }

    SPI_HandleTypeDef& m_hspi;
    GPIO_TypeDef* m_cs_port;
    uint16_t m_cs_pin;
    volatile bool m_data_ready{false};

    alignas(4) std::array<uint8_t, BurstSize + 1> m_tx_cmd_buffer{};
    alignas(4) std::array<uint8_t, BurstSize + 1> m_rx_raw_buffer{};
    std::array<SensorSample, WatermarkSize> m_samples{};
};
