#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "driver/uart.h"
#include "esp_log.h"

#define UART_PORT_NUM      UART_NUM_1
#define BUF_SIZE           256

typedef struct {
    uint16_t cell_voltages[4]; // Напруга комірок у мВ
    uint16_t total_current;    // Струм у мА
    uint16_t temperature;      // Температура в 0.1 K
    uint8_t  fault_flags;      // Прапорці помилок
} bms_telemetry_t;

static uint8_t calculate_checksum(const uint8_t *data, size_t len) {
    uint8_t sum = 0;
    for (size_t i = 0; i < len; i++) {
        sum += data[i];
    }
    return (uint8_t)(~sum + 1);
}

bool parse_bms_frame(const uint8_t *buffer, size_t len, bms_telemetry_t *telemetry) {
    if (len < 13 || buffer[0] != 0xDD || buffer[1] != 0x03) {
        return false; // Невірний заголовок кадру Smart BMS
    }
    
    uint8_t data_len = buffer[2];
    if (len < (size_t)(data_len + 5)) {
        return false; // Кадр неповний
    }
    
    uint8_t crc = calculate_checksum(&buffer[2], data_len + 1);
    if (crc != buffer[data_len + 3]) {
        return false; // Помилка контрольної суми
    }
    
    for (int i = 0; i < 4; i++) {
        telemetry->cell_voltages[i] = (buffer[4 + i * 2] << 8) | buffer[5 + i * 2];
    }
    
    telemetry->fault_flags = buffer[12];
    return true;
}
