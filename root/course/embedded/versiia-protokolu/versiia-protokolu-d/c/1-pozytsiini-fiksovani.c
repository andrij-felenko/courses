#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Специфікація версії 1.0 (8 байтів тіла) */
typedef struct __attribute__((packed)) {
    uint16_t voltage_mv;  /* Offset 0..1 */
    int32_t  current_ma;  /* Offset 2..5 */
    uint16_t status_bits; /* Offset 6..7 */
} TelemetryV1_t;

/* Специфікація версії 1.1 (14 байтів тіла — додано поля в хвіст) */
typedef struct __attribute__((packed)) {
    /* Базові поля v1.0 (зміщення 0..7 повністю збережено!) */
    uint16_t voltage_mv;
    int32_t  current_ma;
    uint16_t status_bits;
    
    /* Нові поля розширення v1.1 */
    int16_t  temperature_c_x100; /* Offset 8..9  (нове) */
    uint32_t system_uptime_sec;  /* Offset 10..13 (нове) */
} TelemetryV2_t;

/* 
 * Функція розбору на новому приймачі (підтримка як v1.0 так і v1.1):
 * Безпечно обробляє пакети будь-якої довжини.
 */
bool parse_telemetry_extended(const uint8_t *payload, uint8_t payload_len, TelemetryV2_t *out) {
    if (payload == NULL || out == NULL || payload_len < sizeof(TelemetryV1_t)) {
        /* Пакет коротший за мінімально допустимий базовий v1.0 */
        return false;
    }
    
    /* 1. Ініціалізуємо всю цільову структуру дефолтними нулями / безпечними значеннями */
    memset(out, 0, sizeof(TelemetryV2_t));
    out->temperature_c_x100 = -32768; /* Маркер відсутності вимірювання температури */
    
    /* 2. Копіюємо стільки байтів, скільки реально прийшло (але не більше ніж розмір нашої структури) */
    uint8_t bytes_to_copy = (payload_len < sizeof(TelemetryV2_t)) ? payload_len : sizeof(TelemetryV2_t);
    memcpy(out, payload, bytes_to_copy);
    
    return true;
}
