#include <Arduino.h>
#include <SPI.h>

struct TelemetryPacket {
    uint32_t timestamp;
    float    temperature;
    uint8_t  fault_code;
    bool     is_valid;
};

uint8_t read_max31865_fault(uint8_t cs_pin) {
    digitalWrite(cs_pin, LOW);
    SPI.transfer(0x07); // Адреса Fault Status Register
    uint8_t fault = SPI.transfer(0x00);
    digitalWrite(cs_pin, HIGH);
    return fault;
}

TelemetryPacket process_logger_sample(uint8_t cs_pin, float raw_rtd) {
    TelemetryPacket packet;
    packet.timestamp = millis();
    packet.fault_code = read_max31865_fault(cs_pin);

    if (packet.fault_code != 0) {
        packet.is_valid = false;
        packet.temperature = NAN;
    } else {
        packet.temperature = rtd_to_temperature(raw_rtd);
        packet.is_valid = !isnan(packet.temperature);
    }
    return packet;
}
