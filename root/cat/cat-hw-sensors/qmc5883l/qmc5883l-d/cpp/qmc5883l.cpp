#include <cstdint>
#include <array>

class QMC5883L {
public:
    static constexpr uint8_t I2C_ADDR = 0x0D;

    enum class Range : uint8_t {
        Gauss2 = 0x00,
        Gauss8 = 0x01
    };

    enum class ODR : uint8_t {
        Hz10  = 0x00,
        Hz50  = 0x01,
        Hz100 = 0x02,
        Hz200 = 0x03
    };

    enum class OSR : uint8_t {
        Samples512 = 0x00,
        Samples256 = 0x01,
        Samples128 = 0x02,
        Samples64  = 0x03
    };

    struct Vector3D {
        int16_t x{0};
        int16_t y{0};
        int16_t z{0};
    };

    virtual bool writeRegister(uint8_t reg, uint8_t value) = 0;
    virtual bool readBytes(uint8_t reg, uint8_t* buffer, uint8_t len) = 0;

    bool begin(OSR osr = OSR::Samples512, Range rng = Range::Gauss2, ODR odr = ODR::Hz200) {
        if (!writeRegister(0x0A, 0x80)) return false; // Soft Reset
        if (!writeRegister(0x0B, 0x01)) return false; // Set/Reset Period
        
        uint8_t ctrl1 = (static_cast<uint8_t>(osr) << 6) |
                        (static_cast<uint8_t>(rng) << 4) |
                        (static_cast<uint8_t>(odr) << 2) |
                        0x01; // Continuous Mode
        return writeRegister(0x09, ctrl1);
    }

    bool readData(Vector3D& outVector) {
        uint8_t status = 0;
        if (!readBytes(0x06, &status, 1) || !(status & 0x01)) {
            return false;
        }

        std::array<uint8_t, 6> rawData{};
        if (!readBytes(0x00, rawData.data(), rawData.size())) {
            return false;
        }

        outVector.x = static_cast<int16_t>(rawData[1] << 8 | rawData[0]);
        outVector.y = static_cast<int16_t>(rawData[3] << 8 | rawData[2]);
        outVector.z = static_cast<int16_t>(rawData[5] << 8 | rawData[4]);
        return true;
    }
};
