#include "Adxl345DmaDriver.hpp"
#include <algorithm>

namespace Sensors {

Adxl345DmaDriver::Adxl345DmaDriver(SPI_HandleTypeDef* hspi,
                                   GPIO_TypeDef* csPort,
                                   uint16_t csPin,
                                   uint16_t int1Pin) noexcept
    : hspi_(hspi), csPort_(csPort), csPin_(csPin), int1Pin_(int1Pin) {
    deselectCs();
}

void Adxl345DmaDriver::selectCs() noexcept {
    HAL_GPIO_WritePin(csPort_, csPin_, GPIO_PIN_RESET);
}

void Adxl345DmaDriver::deselectCs() noexcept {
    HAL_GPIO_WritePin(csPort_, csPin_, GPIO_PIN_SET);
}

bool Adxl345DmaDriver::writeRegister(uint8_t reg, uint8_t value) {
    uint8_t txData[2] = { static_cast<uint8_t>(reg & 0x3F), value };

    CsPinGuard guard(csPort_, csPin_);
    HAL_StatusTypeDef status = HAL_SPI_Transmit(hspi_, txData, 2, HAL_MAX_DELAY);

    return status == HAL_OK;
}

uint8_t Adxl345DmaDriver::readRegister(uint8_t reg) {
    uint8_t txData[2] = { static_cast<uint8_t>(SpiReadBit | (reg & 0x3F)), 0x00 };
    uint8_t rxData[2] = { 0 };

    CsPinGuard guard(csPort_, csPin_);
    HAL_SPI_TransmitReceive(hspi_, txData, rxData, 2, HAL_MAX_DELAY);

    return rxData[1];
}

bool Adxl345DmaDriver::configure(Range range, DataRate rate, uint8_t watermark) {
    // 1. Перевірка DEVID (має відповідати 0xE5)
    uint8_t devId = readRegister(RegDevId);
    if (devId != ExpectedDevId) {
        return false;
    }

    watermarkLevel_ = std::min(watermark, static_cast<uint8_t>(MaxFifoDepth));

    // 2. Встановлення частоти дискретизації (BW_RATE)
    if (!writeRegister(RegBwRate, static_cast<uint8_t>(rate))) {
        return false;
    }

    // 3. Формат даних: FULL_RES (0x08) та діапазон вимірювання
    uint8_t dataFormat = 0x08 | static_cast<uint8_t>(range);
    if (!writeRegister(RegDataFormat, dataFormat)) {
        return false;
    }

    // 4. Налаштування FIFO: режим Stream (0x80) + поріг Watermark
    uint8_t fifoCtl = static_cast<uint8_t>(FifoMode::Stream) | (watermarkLevel_ & 0x1F);
    if (!writeRegister(RegFifoCtl, fifoCtl)) {
        return false;
    }

    // 5. Прив'язка переривання Watermark до лінії INT1 (0 = INT1)
    if (!writeRegister(RegIntMap, 0x00)) {
        return false;
    }

    // 6. Дозвіл переривання Watermark (0x02)
    if (!writeRegister(RegIntEnable, 0x02)) {
        return false;
    }

    // Підготовка TX буфера для пакетного зчитування даних
    txBuffer_.fill(0x00);
    txBuffer_[0] = SpiReadBit | SpiBurstBit | RegDataX0;

    return true;
}

bool Adxl345DmaDriver::start() {
    // Активація режиму вимірювання (Bit 3: Measure у POWER_CTL)
    return writeRegister(RegPowerCtl, 0x08);
}

bool Adxl345DmaDriver::stop() {
    // Перехід у режим Standby
    return writeRegister(RegPowerCtl, 0x00);
}

void Adxl345DmaDriver::onGpioExti(uint16_t gpioPin) noexcept {
    if (gpioPin != int1Pin_) {
        return;
    }

    // Якщо DMA не зайнятий, ініціюємо асинхронну транзакцію
    if (!transferActive_) {
        transferActive_ = true;
        selectCs();

        uint16_t transferSize = static_cast<uint16_t>(1 + watermarkLevel_ * SampleSizeBytes);
        if (HAL_SPI_TransmitReceive_DMA(hspi_, txBuffer_.data(), rxBuffer_.data(), transferSize) != HAL_OK) {
            deselectCs();
            transferActive_ = false;
        }
    }
}

void Adxl345DmaDriver::onSpiTxRxCplt() noexcept {
    if (!transferActive_) {
        return;
    }

    deselectCs();
    transferActive_ = false;

    // Парсинг байтів з буфера RX у масив структур AccelSample
    for (std::size_t i = 0; i < watermarkLevel_; ++i) {
        std::size_t offset = 1 + i * SampleSizeBytes;

        int16_t rawX = static_cast<int16_t>(rxBuffer_[offset] | (rxBuffer_[offset + 1] << 8));
        int16_t rawY = static_cast<int16_t>(rxBuffer_[offset + 2] | (rxBuffer_[offset + 3] << 8));
        int16_t rawZ = static_cast<int16_t>(rxBuffer_[offset + 4] | (rxBuffer_[offset + 5] << 8));

        samples_[i] = AccelSample{ rawX, rawY, rawZ };
    }

    currentSampleCount_ = watermarkLevel_;
    dataReady_ = true;
}

std::span<const AccelSample> Adxl345DmaDriver::getSamples() noexcept {
    return std::span<const AccelSample>(samples_.data(), currentSampleCount_);
}

} // namespace Sensors
