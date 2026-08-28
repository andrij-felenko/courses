#include <stdint.h>

// Пакування внутрішнього та зовнішнього рівнів у 1 байт log_levels
uint8_t pack_log_levels(uint8_t internal_level, uint8_t external_severity) {
    return (uint8_t)(((internal_level & 0x0F) << 4) | (external_severity & 0x0F));
}

// Вилучення внутрішнього рівня (для запису на SD-карту)
uint8_t get_internal_log_level(uint8_t log_levels) {
    return (uint8_t)((log_levels >> 4) & 0x0F);
}

// Вилучення зовнішнього рівня серйозності (для відображення на GCS)
uint8_t get_external_severity(uint8_t log_levels) {
    return (uint8_t)(log_levels & 0x0F);
}
