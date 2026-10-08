#include <stdint.h>

typedef struct {
    uint16_t cell_voltage[6]; // Напруга комірок 1S-6S у мВ
    uint16_t total_current;  // Струм у мА
    uint16_t input_voltage;  // Вхідна напруга у мВ
    int16_t  temperature;    // Температура NTC в 0.1 °C
    uint32_t capacity;       // Ємність у мАг
    uint32_t duration;       // Час у секундах
    uint8_t  work_state;     // Байт стану
    uint8_t  error_code;     // Код помилки
} telemetry_data_t;

void parse_telemetry_frame(const uint8_t *buf, telemetry_data_t *out) {
    if (buf[0] != 0x0F || buf[2] != 0x55) return;
    
    for (int i = 0; i < 6; i++) {
        out->cell_voltage[i] = buf[4 + i * 2] | (buf[5 + i * 2] << 8);
    }
    out->total_current = buf[0x10] | (buf[0x11] << 8);
    out->input_voltage = buf[0x12] | (buf[0x13] << 8);
    out->temperature   = (int16_t)(buf[0x14] | (buf[0x15] << 8));
    out->capacity      = buf[0x16] | (buf[0x17] << 8) | (buf[0x18] << 16) | (buf[0x19] << 24);
    out->duration      = buf[0x1A] | (buf[0x1B] << 8) | (buf[0x1C] << 16) | (buf[0x1D] << 24);
    out->work_state    = buf[0x1E];
    out->error_code    = buf[0x1F];
}
