#include <Wire.h>

#define INA226_I2C_ADDR         0x40
#define INA226_REG_CONFIG       0x00
#define INA226_REG_CURRENT      0x04
#define INA226_REG_CALIBRATION  0x05

class INA226Driver {
private:
    uint8_t _addr;
    float _current_lsb_mA;

    void writeRegister(uint8_t reg, uint16_t value) {
        Wire.beginTransmission(_addr);
        Wire.write(reg);
        Wire.write((value >> 8) & 0xFF);
        Wire.write(value & 0xFF);
        Wire.endTransmission();
    }

    uint16_t readRegister(uint8_t reg) {
        Wire.beginTransmission(_addr);
        Wire.write(reg);
        Wire.endTransmission(false);
        Wire.requestFrom(_addr, (uint8_t)2);
        if (Wire.available() >= 2) {
            return (Wire.read() << 8) | Wire.read();
        }
        return 0;
    }

public:
    INA226Driver(uint8_t addr = INA226_I2C_ADDR) : _addr(addr), _current_lsb_mA(0.1f) {}

    void begin(uint16_t cal_val, float current_lsb_mA) {
        _current_lsb_mA = current_lsb_mA;
        // Записуємо регістр калібрування
        writeRegister(INA226_REG_CALIBRATION, cal_val);
        // Записуємо конфігурацію: усереднення 16 вибірок, режим безперервного вимірювання
        writeRegister(INA226_REG_CONFIG, 0x4527);
    }

    float readCurrentmA() {
        int16_t raw_current = (int16_t)readRegister(INA226_REG_CURRENT);
        return raw_current * _current_lsb_mA;
    }
};
