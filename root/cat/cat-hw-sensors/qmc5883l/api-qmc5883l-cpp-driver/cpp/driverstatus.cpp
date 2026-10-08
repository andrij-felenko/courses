enum class DriverStatus {
    Ok,
    ErrI2C,
    ErrDeviceNotFound,
    ErrInvalidConfig
};

class QMC5883L {
public:
    static constexpr uint8_t I2C_ADDR = 0x0D;

    explicit QMC5883L(II2CAdapter& i2cBus) : m_bus(i2cBus) {}

    DriverStatus init(const QMC5883LConfig& config) {
        // 1. Програмне скидання
        if (!m_bus.writeRegister(I2C_ADDR, 0x0A, 0x80)) {
            return DriverStatus::ErrI2C;
        }

        // Пауза для завершення процедури скидання
        delayMs(5);

        // 2. Обов'язкове налаштування періоду SET/RESET (0x0B = 0x01)
        if (!m_bus.writeRegister(I2C_ADDR, 0x0B, 0x01)) {
            return DriverStatus::ErrI2C;
        }

        // 3. Запис основного регістра конфігурації CR1 (0x09)
        uint8_t cr1Value = config.toControlRegister1();
        if (!m_bus.writeRegister(I2C_ADDR, 0x09, cr1Value)) {
            return DriverStatus::ErrI2C;
        }

        m_currentConfig = config;
        return DriverStatus::Ok;
    }

private:
    II2CAdapter& m_bus;
    QMC5883LConfig m_currentConfig;

    void delayMs(uint32_t ms);
};
