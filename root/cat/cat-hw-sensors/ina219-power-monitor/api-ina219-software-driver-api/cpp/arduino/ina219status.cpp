// Перевірка прапорців CNVR та OVF мовою C++
#include <cstdint>

struct Ina219Status {
    bool isReady;
    bool isOverflow;
    float busVoltageVolts;
};

Ina219Status parseBusRegister(uint16_t rawBusReg) {
    return {
        .isReady = (rawBusReg & 0x0002U) != 0,
        .isOverflow = (rawBusReg & 0x0001U) != 0,
        .busVoltageVolts = static_cast<float>(rawBusReg >> 3) * 0.004f
    };
}
