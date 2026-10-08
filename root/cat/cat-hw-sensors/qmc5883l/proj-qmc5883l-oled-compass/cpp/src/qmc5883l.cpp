#include "qmc5883l.hpp"

QMC5883L::QMC5883L(I2CBus& bus, std::uint8_t address)
    : m_bus(bus), m_address(address) {}

bool QMC5883L::begin(Mode mode, ODR odr, Range range, OSR osr) {
    m_currentRange = range;

    // Крок 1: Програмове скидання пристрою
    if (!softReset()) {
        return false;
    }

    // Крок 2: Запис рекомендованого значення в регістр періоду (Period Register 0x0B = 0x01)
    if (!m_bus.writeRegister(m_address, static_cast<std::uint8_t>(Register::SET_RESET), 0x01)) {
        return false;
    }

    // Крок 3: Формування конфігураційного байта для Control Register 1 (0x09)
    // CR1 = OSR | RNG | ODR | Mode
    std::uint8_t cr1 = static_cast<std::uint8_t>(osr) |
                       static_cast<std::uint8_t>(range) |
                       static_cast<std::uint8_t>(odr) |
                       static_cast<std::uint8_t>(mode);

    if (!m_bus.writeRegister(m_address, static_cast<std::uint8_t>(Register::CONTROL_1), cr1)) {
        return false;
    }

    return true;
}

bool QMC5883L::softReset() {
    // Встановлюємо біт SOFT_RST (0x80) у регістрі Control Register 2 (0x0A)
    return m_bus.writeRegister(m_address, static_cast<std::uint8_t>(Register::CONTROL_2), 0x80);
}

bool QMC5883L::getStatus(StatusFlags& flags) {
    std::uint8_t statusByte = 0;
    if (!m_bus.readRegister(m_address, static_cast<std::uint8_t>(Register::STATUS), statusByte)) {
        return false;
    }

    flags.dataReady = (statusByte & 0x01) != 0; // Біт 0: DRDY
    flags.overflow  = (statusByte & 0x02) != 0; // Біт 1: OVL
    flags.dataSkip  = (statusByte & 0x04) != 0; // Біт 2: DOR

    return true;
}

bool QMC5883L::isDataReady() {
    StatusFlags flags{};
    if (getStatus(flags)) {
        return flags.dataReady;
    }
    return false;
}

bool QMC5883L::readRaw(RawVector3D& raw) {
    // Зчитуємо 6 послідовних регістрів (OUT_X_L ... OUT_Z_H)
    std::array<std::uint8_t, 6> buffer{};
    if (!m_bus.readBytes(m_address, static_cast<std::uint8_t>(Register::OUT_X_L), buffer.data(), buffer.size())) {
        return false;
    }

    // Відліки збережені у форматі Little-Endian зі знаком (2's complement)
    raw.x = static_cast<std::int16_t>(buffer[0] | (buffer[1] << 8));
    raw.y = static_cast<std::int16_t>(buffer[2] | (buffer[3] << 8));
    raw.z = static_cast<std::int16_t>(buffer[4] | (buffer[5] << 8));

    return true;
}

bool QMC5883L::readVector(Vector3D& vec) {
    RawVector3D raw{};
    if (!readRaw(raw)) {
        return false;
    }

    float sensitivity = getSensitivity();
    // Перетворення цілочисельних відліків LSB у Гауси (G)
    vec.x = static_cast<float>(raw.x) / sensitivity;
    vec.y = static_cast<float>(raw.y) / sensitivity;
    vec.z = static_cast<float>(raw.z) / sensitivity;

    return true;
}

float QMC5883L::getSensitivity() const {
    // Згідно з даташитом QMC5883L:
    // 2G -> 12000 LSB / Gauss
    // 8G -> 3000 LSB / Gauss
    switch (m_currentRange) {
        case Range::G2: return 12000.0f;
        case Range::G8: return 3000.0f;
        default:        return 3000.0f;
    }
}
