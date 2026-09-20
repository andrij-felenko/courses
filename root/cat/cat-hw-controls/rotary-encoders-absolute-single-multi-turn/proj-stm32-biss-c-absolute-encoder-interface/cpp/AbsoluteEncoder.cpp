#include "AbsoluteEncoder.h"

AbsoluteEncoder::AbsoluteEncoder(const EncoderConfig& config)
    : m_config(config) {
}

AbsoluteEncoder::~AbsoluteEncoder() = default;

void AbsoluteEncoder::begin() {
    pinMode(m_config.clkPin, OUTPUT);
    digitalWrite(m_config.clkPin, HIGH); // Початковий високий рівень CLK

    pinMode(m_config.dataPin, INPUT_PULLUP);
}

uint32_t AbsoluteEncoder::grayToBinary(uint32_t gray) {
    uint32_t binary = gray;
    while (gray >>= 1) {
        binary ^= gray;
    }
    return binary;
}

uint8_t AbsoluteEncoder::calculateCRC6(uint64_t data, uint8_t bitLength) {
    uint8_t crc = 0x00;
    for (int8_t i = bitLength - 1; i >= 0; --i) {
        uint8_t bit = (data >> i) & 1;
        uint8_t crcMsb = (crc >> 5) & 1;
        crc <<= 1;
        crc &= 0x3F;
        if (crcMsb ^ bit) {
            crc ^= 0x03;
        }
    }
    return crc ^ 0x3F;
}

EncoderFrame AbsoluteEncoder::readFrame() {
    EncoderFrame frame;

    uint8_t totalBits = m_config.multiTurnBits + m_config.singleTurnBits + 2 + 6; // Multi + Single + E + W + CRC6
    uint64_t rawData = 0;

    // Генерація тактових імпульсів та послідовне зчитування бітів
    uint16_t halfPeriod = m_config.clockPeriodUs / 2;
    if (halfPeriod == 0) halfPeriod = 1;

    for (uint8_t i = 0; i < totalBits; ++i) {
        digitalWrite(m_config.clkPin, LOW);
        delayMicroseconds(halfPeriod);
        digitalWrite(m_config.clkPin, HIGH);
        delayMicroseconds(halfPeriod);

        uint8_t bit = (digitalRead(m_config.dataPin) == HIGH) ? 1 : 0;
        rawData = (rawData << 1) | bit;
    }

    // Пауза шини для завершення кадру (monoflop time t_m)
    delayMicroseconds(20);

    // Виділення складових кадру
    // Структура кадру: [MultiTurn][SingleTurn][Error][Warn][CRC6]
    uint8_t receivedCrc = rawData & 0x3F;
    uint64_t payloadAndStatus = rawData >> 6;

    uint8_t payloadBits = m_config.multiTurnBits + m_config.singleTurnBits + 2;
    uint8_t computedCrc = calculateCRC6(payloadAndStatus, payloadBits);

    frame.crcValid = (receivedCrc == computedCrc);

    uint8_t warnBit = (payloadAndStatus >> 0) & 1;
    uint8_t errBit = (payloadAndStatus >> 1) & 1;

    // Зазвичай в BiSS/SSI біти помилки активні в LOW (0 = Error)
    frame.statusErr = (errBit == 0);
    frame.statusWarn = (warnBit == 0);

    uint64_t posData = payloadAndStatus >> 2;
    uint32_t singleTurnMask = (1UL << m_config.singleTurnBits) - 1;
    uint32_t multiTurnMask = (1UL << m_config.multiTurnBits) - 1;

    uint32_t rawSingleTurn = posData & singleTurnMask;
    uint32_t rawMultiTurn = (posData >> m_config.singleTurnBits) & multiTurnMask;

    if (m_config.useGrayCode) {
        frame.singleTurnPosition = grayToBinary(rawSingleTurn);
        frame.multiTurnCount = grayToBinary(rawMultiTurn);
    } else {
        frame.singleTurnPosition = rawSingleTurn;
        frame.multiTurnCount = rawMultiTurn;
    }

    frame.valid = frame.crcValid && !frame.statusErr;
    return frame;
}
