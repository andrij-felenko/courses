#include <Wire.h>

#define OV2640_SCCB_ADDR 0x30

struct RegisterSetting {
    uint8_t reg;
    uint8_t val;
};

const RegisterSetting ov2640_init_script[] = {
    {0xFF, 0x01}, // Перемикання на Sensor bank
    {0x12, 0x80}, // Програмний скид (soft reset)
    {0xFF, 0x00}, // Перемикання на DSP bank
    {0x2C, 0xFF}, // Конфігурація вихідних стробів
    {0x2E, 0xDF}, // Налаштування FIFO
    {0x00, 0x00}  // Маркер закінчення
};

bool writeRegisterArray(const RegisterSetting* table) {
    for (size_t i = 0; table[i].reg != 0x00 || table[i].val != 0x00; ++i) {
        Wire.beginTransmission(OV2640_SCCB_ADDR);
        Wire.write(table[i].reg);
        Wire.write(table[i].val);
        if (Wire.endTransmission() != 0) {
            return false;
        }
        if (table[i].reg == 0x12 && table[i].val == 0x80) {
            delay(10);
        }
    }
    return true;
}
