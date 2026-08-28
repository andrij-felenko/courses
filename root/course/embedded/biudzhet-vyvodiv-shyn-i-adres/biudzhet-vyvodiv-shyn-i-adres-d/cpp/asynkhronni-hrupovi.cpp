#include <cstdint>
#include <expected>

struct ExpanderEvent {
    uint8_t triggeredMask;  /* Біти пінів, які змінили стан */
    uint8_t capturedValues; /* Значення на пінах у момент генерації переривання */
};

class Mcp23017Driver {
public:
    enum class Error { I2cFailure, ConfigError };

    explicit Mcp23017Driver(uint8_t i2cAddr) : addr_(i2cAddr) {}

    std::expected<void, Error> configureInterruptInputs(uint8_t pinMask) {
        if (!writeRegister(0x00 /* IODIRA */, pinMask)) {
            return std::unexpected(Error::I2cFailure);
        }
        if (!writeRegister(0x04 /* GPINTENA */, pinMask)) {
            return std::unexpected(Error::I2cFailure);
        }
        /* Скидаємо початковий стан переривань */
        uint8_t dummy = 0;
        (void)readRegister(0x12 /* GPIOA */, dummy);
        return {};
    }

    std::expected<ExpanderEvent, Error> readAndClearInterrupt() {
        uint8_t flags = 0;
        uint8_t captured = 0;

        if (!readRegister(0x0E /* INTFA */, flags)) {
            return std::unexpected(Error::I2cFailure);
        }
        /* Зчитування INTCAP фіксує стан і апаратно відпускає лінію INT */
        if (!readRegister(0x10 /* INTCAPA */, captured)) {
            return std::unexpected(Error::I2cFailure);
        }

        return ExpanderEvent{flags, captured};
    }

private:
    uint8_t addr_;

    bool writeRegister(uint8_t reg, uint8_t val) {
        extern bool platform_i2c_write(uint8_t dev, uint8_t r, uint8_t v);
        return platform_i2c_write(addr_, reg, val);
    }

    bool readRegister(uint8_t reg, uint8_t& val) {
        extern bool platform_i2c_read(uint8_t dev, uint8_t r, uint8_t* v);
        return platform_i2c_read(addr_, reg, &val);
    }
};
