#include <stdint.h>
#include <stdio.h>

typedef struct {
    int32_t actual_position_counts;
    float actual_velocity_rpm;
    float phase_current_amps;
    float bus_voltage_volts;
    float mosfet_temp_celsius;
} TelemetryDataSI;

// Декодування сирого масиву телеметричних регістрів у фізичні величини
void parse_telemetry_packet(const uint8_t *raw_payload, TelemetryDataSI *out_telemetry) {
    // 1. Поточна позиція (32 біти, 0x6064)
    int32_t raw_pos = (int32_t)((uint32_t)raw_payload[0] |
                               ((uint32_t)raw_payload[1] << 8) |
                               ((uint32_t)raw_payload[2] << 16) |
                               ((uint32_t)raw_payload[3] << 24));
    out_telemetry->actual_position_counts = raw_pos;

    // 2. Поточна швидкість (16 біт, об/хв)
    int16_t raw_vel = (int16_t)((uint16_t)raw_payload[4] | ((uint16_t)raw_payload[5] << 8));
    out_telemetry->actual_velocity_rpm = (float)raw_vel;

    // 3. Фазовий струм (16 біт, мА -> А)
    int16_t raw_curr = (int16_t)((uint16_t)raw_payload[6] | ((uint16_t)raw_payload[7] << 8));
    out_telemetry->phase_current_amps = (float)raw_curr / 1000.0f;

    // 4. Напруга шини (16 біт, мВ -> В)
    uint16_t raw_volt = (uint16_t)((uint16_t)raw_payload[8] | ((uint16_t)raw_payload[9] << 8));
    out_telemetry->bus_voltage_volts = (float)raw_volt / 1000.0f;

    // 5. Температура MOSFET (16 біт, 0.1 °C -> °C)
    int16_t raw_temp = (int16_t)((uint16_t)raw_payload[10] | ((uint16_t)raw_payload[11] << 8));
    out_telemetry->mosfet_temp_celsius = (float)raw_temp / 10.0f;
}
