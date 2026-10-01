#include <stdint.h>
#include <stdbool.h>

// Перевірка обмеження частоти відправки даних (Rate Limiting)
bool check_rate_limit(uint32_t *last_send_ms, uint32_t current_ms, uint32_t min_interval_ms) {
    if (current_ms - *last_send_ms < min_interval_ms) {
        return false; // Відправку заблоковано для захисту буферів DRAM
    }
    *last_send_ms = current_ms;
    return true;
}

// Проста перевірка контрольної суми пакета (CRC8)
uint8_t calculate_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0x00;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
    }
    return crc;
}
