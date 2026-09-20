#include "dip_config.hpp"

DipConfig::DipConfig(uint8_t rawByte)
    : m_rawByte(rawByte) {}

uint8_t DipConfig::getRawByte() const {
    return m_rawByte;
}

uint8_t DipConfig::getDeviceAddress() const {
    // Накладання побітової маски 0b00000111 для виділення молодших 3 бітів
    return m_rawByte & MASK_ADDRESS;
}

BaudRate DipConfig::getBaudRate() const {
    // Маскування бітів 3..4 та правий зсув на 3 позиції
    uint8_t baudRaw = (m_rawByte & MASK_BAUD) >> SHIFT_BAUD;
    return static_cast<BaudRate>(baudRaw);
}

OperatingMode DipConfig::getOperatingMode() const {
    // Маскування бітів 5..6 та правий зсув на 5 позицій
    uint8_t modeRaw = (m_rawByte & MASK_MODE) >> SHIFT_MODE;
    return static_cast<OperatingMode>(modeRaw);
}

bool DipConfig::calculateParity() const {
    // Обчислення додаванням за модулем 2 (XOR) усіх 7 інформаційних бітів (0..6)
    uint8_t dataBits = m_rawByte & 0x7F; // Відсікаємо біт парності (біт 7)
    uint8_t parity = 0;
    
    for (int i = 0; i < 7; ++i) {
        parity ^= (dataBits >> i) & 0x01;
    }
    
    return parity != 0;
}

bool DipConfig::isParityValid() const {
    // Витягуємо отриманий біт парності зі старшого розряду [7]
    bool receivedParity = ((m_rawByte & MASK_PARITY) >> SHIFT_PARITY) != 0;
    // Звіряємо обчислений паритет із отриманим
    return calculateParity() == receivedParity;
}

bool DipConfig::parse(ConfigSettings& outSettings) const {
    // 1. Перевірка цілісності даних через біт парності
    outSettings.parityValid = isParityValid();
    if (!outSettings.parityValid) {
        return false;
    }

    // 2. Витягнення та заповнення полів
    outSettings.deviceAddress = getDeviceAddress();
    outSettings.baudRate = getBaudRate();
    outSettings.mode = getOperatingMode();

    // 3. Додаткова валідація режимів роботи (Reserved вважається недопустимим)
    if (outSettings.mode == OperatingMode::Reserved) {
        return false;
    }

    return true;
}
