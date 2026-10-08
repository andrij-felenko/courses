#include <cstdint>

enum class QMC5883L_ODR : uint8_t {
    Hz10  = 0x00, // 00b -> 10 Гц
    Hz50  = 0x04, // 01b -> 50 Гц (зсунуто на 2 біти)
    Hz100 = 0x08, // 10b -> 100 Гц
    Hz200 = 0x0C  // 11b -> 200 Гц
};

enum class QMC5883L_Range : uint8_t {
    Gauss2 = 0x00, // 00b -> ±2 Гаус (4096 LSB/G)
    Gauss8 = 0x10  // 01b -> ±8 Гаус (1024 LSB/G, зсунуто на 4 біти)
};

enum class QMC5883L_OSR : uint8_t {
    Ratio512 = 0x00, // 00b -> 512 усереднень
    Ratio256 = 0x40, // 01b -> 256 усереднень (зсунуто на 6 бітів)
    Ratio128 = 0x80, // 10b -> 128 усереднень
    Ratio64  = 0xC0  // 11b -> 64 усереднення
};

enum class QMC5883L_Mode : uint8_t {
    Standby    = 0x00, // 00b -> Режим сну
    Continuous = 0x01  // 01b -> Безперервні вимірювання
};

struct QMC5883LConfig {
    QMC5883L_ODR   odr   = QMC5883L_ODR::Hz100;
    QMC5883L_Range range = QMC5883L_Range::Gauss2;
    QMC5883L_OSR   osr   = QMC5883L_OSR::Ratio512;
    QMC5883L_Mode  mode  = QMC5883L_Mode::Continuous;

    uint8_t toControlRegister1() const {
        return static_cast<uint8_t>(odr) |
               static_cast<uint8_t>(range) |
               static_cast<uint8_t>(osr) |
               static_cast<uint8_t>(mode);
    }
};
