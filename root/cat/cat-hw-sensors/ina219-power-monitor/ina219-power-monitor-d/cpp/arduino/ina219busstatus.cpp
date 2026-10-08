// Зчитування регістра 02h та обробка прапорців CNVR і OVF
#include <Arduino.h>

struct Ina219BusStatus {
    uint16_t busVoltageRaw;
    bool conversionReady;
    bool mathOverflow;
};

Ina219BusStatus parseBusVoltageRegister(uint16_t reg02hValue) {
    Ina219BusStatus status;
    // Старші 13 бітів (15..3) містять напругу шини (LSB = 4 мВ)
    status.busVoltageRaw = reg02hValue >> 3;
    // Біт 1: Conversion Ready (CNVR)
    status.conversionReady = (reg02hValue & (1U << 1)) != 0;
    // Біт 0: Math Overflow (OVF)
    status.mathOverflow = (reg02hValue & (1U << 0)) != 0;
    return status;
}
