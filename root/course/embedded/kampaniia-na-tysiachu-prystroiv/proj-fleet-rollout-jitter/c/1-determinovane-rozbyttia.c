#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define HW_ID_LEN 16
#define SALT_LEN  16

/* Спрощена ілюстративна хеш-функція типу FNV-1a для MCU
   У промислових виробах використовується апаратний SHA-256 */
static uint32_t compute_hash32(const uint8_t *data, size_t len) {
    uint32_t hash = 2166136261u;
    for (size_t i = 0; i < len; ++i) {
        hash ^= data[i];
        hash *= 16777619u;
    }
    return hash;
}

uint8_t calculate_device_cohort(const uint8_t hw_id[HW_ID_LEN],
                                const uint8_t salt[SALT_LEN]) {
    uint8_t buffer[HW_ID_LEN + SALT_LEN];
    memcpy(buffer, hw_id, HW_ID_LEN);
    memcpy(buffer + HW_ID_LEN, salt, SALT_LEN);

    uint32_t digest = compute_hash32(buffer, sizeof(buffer));
    return (uint8_t)(digest % 100u);
}

bool is_device_eligible_for_stage(uint8_t device_cohort, uint8_t stage_cutoff_percent) {
    return device_cohort < stage_cutoff_percent;
}
