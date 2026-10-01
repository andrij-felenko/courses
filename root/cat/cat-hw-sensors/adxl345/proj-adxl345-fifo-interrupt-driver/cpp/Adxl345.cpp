#include "Adxl345.hpp"
#include <algorithm>
#include <cmath>

namespace adxl345 {

ADXL345::ADXL345(IBus& bus)
    : bus_(bus) {}

bool ADXL345::init(Range range, bool fullResolution) {
    uint8_t devId = 0;
    if (!bus_.readRegister(Register::DEVID, devId)) {
        return false;
    }

    // Перевірка ідентифікатора пристрою
    if (devId != ADXL345_EXPECTED_DEVID) {
        return false;
    }

    // Переведення у Standby для зміни конфігураційних регістрів
    if (!setMeasurementMode(false)) {
        return false;
    }

    range_ = range;
    fullRes_ = fullResolution;
    updateScaleFactor();

    // Формування значення регістра DATA_FORMAT
    uint8_t dataFormat = static_cast<uint8_t>(range_);
    if (fullRes_) {
        dataFormat |= DataFormatBit::FULL_RES;
    }

    if (!bus_.writeRegister(Register::DATA_FORMAT, dataFormat)) {
        return false;
    }

    // Ввімкнення режиму вимірювання
    return setMeasurementMode(true);
}

bool ADXL345::configureFifo(FifoMode mode, uint8_t watermarkLevel) {
    // Рівень Watermark обмежено діапазоном від 1 до 31 кадрів
    uint8_t clampedWatermark = std::clamp<uint8_t>(watermarkLevel, 1, 31);
    uint8_t fifoModeBits = static_cast<uint8_t>(mode) << 6;
    uint8_t fifoCtlVal = fifoModeBits | (clampedWatermark & 0x1F);

    if (!bus_.writeRegister(Register::FIFO_CTL, fifoCtlVal)) {
        return false;
    }

    // Конфігурація переривань в залежності від режиму FIFO
    uint8_t intEnable = 0;
    if (mode == FifoMode::Fifo || mode == FifoMode::Stream || mode == FifoMode::Trigger) {
        intEnable |= (IntBit::WATERMARK | IntBit::OVERRUN);
    } else {
        intEnable |= IntBit::DATA_READY;
    }

    return bus_.writeRegister(Register::INT_ENABLE, intEnable);
}

bool ADXL345::setMeasurementMode(bool enable) {
    uint8_t powerCtl = 0;
    if (!bus_.readRegister(Register::POWER_CTL, powerCtl)) {
        return false;
    }

    if (enable) {
        powerCtl |= PowerCtlBit::MEASURE;
    } else {
        powerCtl &= ~PowerCtlBit::MEASURE;
    }

    return bus_.writeRegister(Register::POWER_CTL, powerCtl);
}

void ADXL345::registerCallback(Event event, EventCallback callback) {
    if (callback) {
        callbacks_[event] = std::move(callback);
    } else {
        callbacks_.erase(event);
    }
}

bool ADXL345::getFifoEntryCount(uint8_t& count) {
    uint8_t fifoStatus = 0;
    if (!bus_.readRegister(Register::FIFO_STATUS, fifoStatus)) {
        count = 0;
        return false;
    }
    // Маска кількості кадрів [4:0]
    count = fifoStatus & 0x1F;
    return true;
}

bool ADXL345::readFifoBurst(std::span<AccelData> outputBuffer, size_t& readCount) {
    readCount = 0;
    uint8_t entries = 0;
    if (!getFifoEntryCount(entries) || entries == 0) {
        return true;
    }

    size_t countToRead = std::min(static_cast<size_t>(entries), outputBuffer.size());
    if (countToRead == 0) {
        return true;
    }

    // Буфер для пакетного зчитування сирих 6-байтних кадрів (X0, X1, Y0, Y1, Z0, Z1)
    std::array<uint8_t, 32 * 6> rawBuffer{};
    std::span<uint8_t> targetSpan(rawBuffer.data(), countToRead * 6);

    // Виконання burst read починаючи з регістра DATAX0 (0x32)
    if (!bus_.readBurst(Register::DATAX0, targetSpan)) {
        return false;
    }

    for (size_t i = 0; i < countToRead; ++i) {
        size_t idx = i * 6;
        int16_t rawX = static_cast<int16_t>(rawBuffer[idx] | (rawBuffer[idx + 1] << 8));
        int16_t rawY = static_cast<int16_t>(rawBuffer[idx + 2] | (rawBuffer[idx + 3] << 8));
        int16_t rawZ = static_cast<int16_t>(rawBuffer[idx + 4] | (rawBuffer[idx + 5] << 8));

        outputBuffer[i] = convertRawToG(rawX, rawY, rawZ);
    }

    readCount = countToRead;
    return true;
}

bool ADXL345::readSingleSample(AccelData& sample) {
    std::array<uint8_t, 6> rawData{};
    if (!bus_.readBurst(Register::DATAX0, rawData)) {
        return false;
    }

    int16_t rawX = static_cast<int16_t>(rawData[0] | (rawData[1] << 8));
    int16_t rawY = static_cast<int16_t>(rawData[2] | (rawData[3] << 8));
    int16_t rawZ = static_cast<int16_t>(rawData[4] | (rawData[5] << 8));

    sample = convertRawToG(rawX, rawY, rawZ);
    return true;
}

bool ADXL345::processInterrupts() {
    uint8_t intSource = 0;
    if (!bus_.readRegister(Register::INT_SOURCE, intSource)) {
        return false;
    }

    // Перевірка переповнення буфера (Overrun)
    if (intSource & IntBit::OVERRUN) {
        auto it = callbacks_.find(Event::Overrun);
        if (it != callbacks_.end()) {
            it->second(Event::Overrun, {});
        }
    }

    // Перевірка досягнення рівня Watermark у FIFO
    if (intSource & IntBit::WATERMARK) {
        size_t readCount = 0;
        if (readFifoBurst(internalBuffer_, readCount) && readCount > 0) {
            auto it = callbacks_.find(Event::Watermark);
            if (it != callbacks_.end()) {
                it->second(Event::Watermark, std::span<const AccelData>(internalBuffer_.data(), readCount));
            }
        }
    }

    // Перевірка наявності поодиноких даних у режимі Bypass
    if (intSource & IntBit::DATA_READY) {
        AccelData sample{};
        if (readSingleSample(sample)) {
            auto it = callbacks_.find(Event::DataReady);
            if (it != callbacks_.end()) {
                it->second(Event::DataReady, std::span<const AccelData>(&sample, 1));
            }
        }
    }

    return true;
}

void ADXL345::updateScaleFactor() {
    if (fullRes_) {
        // У режимі Full Resolution масштабуючий коефіцієнт сталий: ~3.9 mg/LSB (0.00390625 g/LSB)
        scaleFactor_ = 0.00390625f;
    } else {
        // У 10-бітному режимі роздільна здатність залежить від обраного розмаху
        switch (range_) {
            case Range::Range_2G:  scaleFactor_ = 0.00390625f; break; // 1 / 256 g/LSB
            case Range::Range_4G:  scaleFactor_ = 0.00781250f; break; // 1 / 128 g/LSB
            case Range::Range_8G:  scaleFactor_ = 0.01562500f; break; // 1 / 64 g/LSB
            case Range::Range_16G: scaleFactor_ = 0.03125000f; break; // 1 / 32 g/LSB
        }
    }
}

AccelData ADXL345::convertRawToG(int16_t rawX, int16_t rawY, int16_t rawZ) const {
    return AccelData{
        .x = static_cast<float>(rawX) * scaleFactor_,
        .y = static_cast<float>(rawY) * scaleFactor_,
        .z = static_cast<float>(rawZ) * scaleFactor_
    };
}

} // namespace adxl345
