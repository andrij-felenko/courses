#include "max31865_sensor.hpp"
#include "rtd_math.hpp"

RtdFaultGuard::RtdFaultGuard(MAX31865Sensor& sensor)
    : sensor_(&sensor), active_(true) {
    cached_fault_ = sensor_->readFaultRegister();
}

RtdFaultGuard::~RtdFaultGuard() {
    if (active_ && sensor_ && cached_fault_.anyFault()) {
        sensor_->clearFaultRegister();
    }
}

RtdFaultGuard::RtdFaultGuard(RtdFaultGuard&& other) noexcept
    : sensor_(other.sensor_), cached_fault_(other.cached_fault_), active_(other.active_) {
    other.sensor_ = nullptr;
    other.active_ = false;
}

RtdFaultGuard& RtdFaultGuard::operator=(RtdFaultGuard&& other) noexcept {
    if (this != &other) {
        if (active_ && sensor_ && cached_fault_.anyFault()) {
            sensor_->clearFaultRegister();
        }
        sensor_ = other.sensor_;
        cached_fault_ = other.cached_fault_;
        active_ = other.active_;
        other.sensor_ = nullptr;
        other.active_ = false;
    }
    return *this;
}

void RtdFaultGuard::clearAndReset() {
    if (sensor_) {
        sensor_->clearFaultRegister();
        cached_fault_ = sensor_->readFaultRegister();
    }
}

MAX31865Sensor::MAX31865Sensor(SpiTransferFn spi_transfer, GpioWriteFn cs_write, GetTickMsFn get_tick_ms)
    : spi_transfer_(std::move(spi_transfer)), cs_write_(std::move(cs_write)), get_tick_ms_(std::move(get_tick_ms)) {
    if (cs_write_) {
        cs_write_(true); // Неактивний стан CS (High)
    }
}

uint8_t MAX31865Sensor::readRegister(uint8_t reg) {
    uint8_t tx_buf[2] = { static_cast<uint8_t>(reg & 0x7F), 0x00 };
    uint8_t rx_buf[2] = { 0, 0 };

    if (cs_write_) cs_write_(false);
    bool ok = spi_transfer_(tx_buf, rx_buf, 2);
    if (cs_write_) cs_write_(true);

    return ok ? rx_buf[1] : 0;
}

bool MAX31865Sensor::writeRegister(uint8_t reg, uint8_t value) {
    uint8_t tx_buf[2] = { static_cast<uint8_t>(reg | 0x80), value };
    uint8_t rx_buf[2] = { 0, 0 };

    if (cs_write_) cs_write_(false);
    bool ok = spi_transfer_(tx_buf, rx_buf, 2);
    if (cs_write_) cs_write_(true);

    return ok;
}

bool MAX31865Sensor::readRegisters(uint8_t start_reg, uint8_t* buffer, size_t length) {
    if (!buffer || length == 0) return false;

    // Створюємо тимчасовий буфер для передачі адреси та dummy-байтів
    std::array<uint8_t, 16> tx_buf{};
    std::array<uint8_t, 16> rx_buf{};
    if (length + 1 > tx_buf.size()) return false;

    tx_buf[0] = start_reg & 0x7F;

    if (cs_write_) cs_write_(false);
    bool ok = spi_transfer_(tx_buf.data(), rx_buf.data(), length + 1);
    if (cs_write_) cs_write_(true);

    if (ok) {
        for (size_t i = 0; i < length; ++i) {
            buffer[i] = rx_buf[i + 1];
        }
    }
    return ok;
}

bool MAX31865Sensor::begin(const RtdConfig& config) {
    config_ = config;

    // Формування початкового регістра конфігурації
    uint8_t cfg = 0;
    if (config_.wire_mode == WireMode::ThreeWire) {
        cfg |= CONFIG_3WIRE;
    }
    if (config_.filter == FilterFrequency::Hz50) {
        cfg |= CONFIG_FILTER_50HZ;
    }

    // Запис регістра конфігурації та примусове скидання прапорців помилок
    cfg |= CONFIG_FAULT_CLEAR;
    if (!writeRegister(REG_CONFIG, cfg)) {
        state_ = SensorState::FaultDetected;
        return false;
    }

    // Запис порогів автоматичної діагностики тривог
    writeRegister(REG_HIGH_FAULT_MSB, static_cast<uint8_t>(config_.high_threshold_adc >> 8));
    writeRegister(REG_HIGH_FAULT_LSB, static_cast<uint8_t>(config_.high_threshold_adc & 0xFF));
    writeRegister(REG_LOW_FAULT_MSB, static_cast<uint8_t>(config_.low_threshold_adc >> 8));
    writeRegister(REG_LOW_FAULT_LSB, static_cast<uint8_t>(config_.low_threshold_adc & 0xFF));

    state_ = SensorState::Idle;
    drdy_pending_ = false;
    return true;
}

bool MAX31865Sensor::startAsyncConversion() {
    if (state_ == SensorState::Uninitialized) {
        return false;
    }

    // Зчитуємо поточну конфігурацію
    uint8_t cfg = readRegister(REG_CONFIG);

    // Увімкнення генератора струму VBIAS
    cfg |= CONFIG_VBIAS;
    if (!writeRegister(REG_CONFIG, cfg)) {
        state_ = SensorState::FaultDetected;
        return false;
    }

    bias_start_ticks_ = get_tick_ms_();
    state_ = SensorState::BiasStabilizing;
    drdy_pending_ = false;
    return true;
}

void MAX31865Sensor::handleExtiInterrupt() noexcept {
    drdy_pending_ = true;
}

void MAX31865Sensor::processFsm() {
    uint32_t now = get_tick_ms_();

    switch (state_) {
    case SensorState::BiasStabilizing:
        // Перевірка часу стабілізації VBIAS (мінімум 10 мс)
        if (now - bias_start_ticks_ >= 10) {
            uint8_t cfg = readRegister(REG_CONFIG);
            cfg |= CONFIG_VBIAS | CONFIG_1SHOT; // Запуск 1-Shot перетворення
            writeRegister(REG_CONFIG, cfg);

            conversion_start_ticks_ = now;
            state_ = SensorState::Converting;
        }
        break;

    case SensorState::Converting:
        // Перевірка надходження сигналів переривання EXTI від DRDY або таймауту (100 мс)
        if (drdy_pending_ || (now - conversion_start_ticks_ >= 100)) {
            drdy_pending_ = false;
            state_ = SensorState::DataReady;
        }
        break;

    case SensorState::DataReady: {
        // Зчитування 2 байтів АЦП (0x01 MSB, 0x02 LSB) та 1 байта помилок (0x07)
        uint8_t rtd_data[2] = {0, 0};
        if (!readRegisters(REG_RTD_MSB, rtd_data, 2)) {
            state_ = SensorState::FaultDetected;
            break;
        }

        uint16_t raw_adc = ((static_cast<uint16_t>(rtd_data[0]) << 8) | rtd_data[1]) >> 1;
        bool fault_bit = (rtd_data[1] & 0x01) != 0;

        FaultFlags fault_flags = readFaultRegister();

        // Якщо встановлено біт помилки в LSB, але регістр 0x07 порожній, фіксуємо зауваження
        if (fault_bit && !fault_flags.anyFault()) {
            fault_flags.over_under_voltage = true;
        }

        latest_telemetry_ = RtdMath::convertAdcToTelemetry(raw_adc, config_, fault_flags, now);

        // Вимкнення VBIAS для економії енергії та зменшення самонагріву RTD
        uint8_t cfg = readRegister(REG_CONFIG);
        cfg &= ~CONFIG_VBIAS;
        writeRegister(REG_CONFIG, cfg);

        if (fault_flags.anyFault()) {
            state_ = SensorState::FaultDetected;
        } else {
            state_ = SensorState::Idle;
        }
        break;
    }

    case SensorState::FaultDetected:
    case SensorState::Idle:
    case SensorState::Uninitialized:
    default:
        break;
    }
}

FaultFlags MAX31865Sensor::readFaultRegister() {
    uint8_t raw = readRegister(REG_FAULT_STATUS);
    FaultFlags flags{};
    flags.raw_byte = raw;
    flags.high_threshold_exceeded      = (raw & (1 << 7)) != 0;
    flags.low_threshold_exceeded       = (raw & (1 << 6)) != 0;
    flags.refin_greater_than_085_vbias = (raw & (1 << 5)) != 0;
    flags.refin_less_than_085_vbias    = (raw & (1 << 4)) != 0;
    flags.rtdin_less_than_085_vbias    = (raw & (1 << 3)) != 0;
    flags.over_under_voltage           = (raw & (1 << 2)) != 0;
    return flags;
}

bool MAX31865Sensor::clearFaultRegister() {
    uint8_t cfg = readRegister(REG_CONFIG);
    cfg |= CONFIG_FAULT_CLEAR;
    bool ok = writeRegister(REG_CONFIG, cfg);
    if (ok && state_ == SensorState::FaultDetected) {
        state_ = SensorState::Idle;
    }
    return ok;
}

std::optional<RtdTelemetry> MAX31865Sensor::getLatestTelemetry() const noexcept {
    if (state_ == SensorState::Uninitialized) {
        return std::nullopt;
    }
    return latest_telemetry_;
}
