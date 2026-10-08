// Зчитування магнітного енкодера через SPI та перевірка парності у C++ (Arduino)
#include <Arduino.h>
#include <SPI.h>

const int CS_PIN = 10;
const uint16_t ANGLE_REG = 0x3FFF;
const uint16_t READ_CMD_FLAG = 0x4000;
const uint16_t PARITY_MASK = 0x8000;

bool check_parity_cpp(uint16_t val) {
    uint16_t cnt = 0;
    for (int i = 0; i < 16; i++) {
        if (val & (1 << i)) cnt++;
    }
    return (cnt % 2) != 0;
}

float read_magnetic_encoder_angle_arduino() {
    uint16_t cmd = ANGLE_REG | READ_CMD_FLAG;
    if (check_parity_cpp(cmd)) {
        cmd |= PARITY_MASK;
    }

    digitalWrite(CS_PIN, LOW);
    uint8_t msb = SPI.transfer(highByte(cmd));
    uint8_t lsb = SPI.transfer(lowByte(cmd));
    digitalWrite(CS_PIN, HIGH);

    uint16_t rx_data = ((uint16_t)msb << 8) | lsb;

    if (check_parity_cpp(rx_data & 0x7FFF) != ((rx_data & PARITY_MASK) >> 15)) {
        return -1.0f; // Помилка парності кадру SPI
    }

    uint16_t raw_angle = rx_data & 0x3FFF;
    return ((float)raw_angle * 360.0f) / 16384.0f;
}
