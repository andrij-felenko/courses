// Стійке зчитування даних з обробкою помилок мовою C++
#include <cstdint>

enum class Ina219Status {
    Success,
    I2cError,
    Overflow,
    Timeout
};

struct PowerMetrics {
    float voltageVolts;
    float currentAmps;
    float powerWatts;
};

class Ina219Driver {
public:
    Ina219Driver(uint8_t address, float currentLsb, float powerLsb)
        : m_addr(address), m_currentLsb(currentLsb), m_powerLsb(powerLsb) {}

    Ina219Status readMetrics(PowerMetrics& metrics) {
        uint16_t busReg = 0;
        if (!readRegisterWithRetry(0x02, busReg, 3)) {
            return Ina219Status::I2cError;
        }

        if (busReg & 0x0001U) { // OVF check
            return Ina219Status::Overflow;
        }

        uint16_t currentReg = 0, powerReg = 0;
        if (!readRegisterWithRetry(0x04, currentReg, 3) ||
            !readRegisterWithRetry(0x03, powerReg, 3)) {
            return Ina219Status::I2cError;
        }

        metrics.voltageVolts = static_cast<float>(busReg >> 3) * 0.004f;
        metrics.currentAmps = static_cast<float>(static_cast<int16_t>(currentReg)) * m_currentLsb;
        metrics.powerWatts = static_cast<float>(powerReg) * m_powerLsb;

        return Ina219Status::Success;
    }

private:
    uint8_t m_addr;
    float m_currentLsb;
    float m_powerLsb;

    bool readRegisterWithRetry(uint8_t reg, uint16_t& val, int retries) {
        // Заглушка виклику апаратного I2C
        return true; 
    }
};
