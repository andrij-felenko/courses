#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    uint32_t id;
    uint32_t time_boot_ms;
    uint16_t sequence;
    uint8_t  internal_log_level;
    uint8_t  external_severity;
    char     display_text[256];
    char     action_text[256];
} formatted_event_t;

// Декодування та форматування події збою калібрування компаса (0x8A12B4C0)
bool decode_and_format_event(const uint8_t *raw_payload,
                             size_t payload_len,
                             formatted_event_t *out_event) {
    if (payload_len < 13 + sizeof(uint8_t) + sizeof(float)) {
        return false;
    }

    uint32_t id;
    memcpy(&id, &raw_payload[0], sizeof(uint32_t));
    if (id != 0x8A12B4C0) {
        return false; // Невідомий або інший event_id
    }

    out_event->id = id;
    memcpy(&out_event->time_boot_ms, &raw_payload[4], sizeof(uint32_t));
    memcpy(&out_event->sequence, &raw_payload[8], sizeof(uint16_t));

    uint8_t log_levels = raw_payload[12];
    out_event->internal_log_level = (log_levels >> 4) & 0x0F;
    out_event->external_severity = log_levels & 0x0F;

    const uint8_t *args = &raw_payload[13];
    uint8_t sensor_id = unpack_u8(args, 0);
    float deviation = unpack_f32_le(args, 1);

    // Підстановка аргументів у локалізований рядок українською мовою
    snprintf(out_event->display_text, sizeof(out_event->display_text),
             "Збій калібрування компаса №%u (відхилення: %.1f°)",
             sensor_id, deviation);

    snprintf(out_event->action_text, sizeof(out_event->action_text),
             "Відійдіть на 15 метрів від металевих конструкцій та повторіть процедуру.");

    return true;
}
