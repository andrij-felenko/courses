/* strapping_check.c - валідація конфігурації strapping-пінів */
#include <stdio.h>
#include <stdbool.h>

typedef enum {
    PULL_NONE,
    PULL_UP_VCC,
    PULL_DOWN_GND
} PinPullMode;

typedef struct {
    const char *pin_name;
    PinPullMode pull;
    bool required_level_high;
    const char *critical_role;
} StrappingPinConfig;

bool audit_strapping_pins(const StrappingPinConfig *pins, size_t count) {
    printf("=== АУДИТ КОНФІГУРАЦІЙНИХ ВИВОДІВ (STRAPPING PINS) ===\n");
    bool all_valid = true;

    for (size_t i = 0; i < count; ++i) {
        bool actual_level_high = (pins[i].pull == PULL_UP_VCC);
        bool pull_present = (pins[i].pull != PULL_NONE);

        printf("Пін %s [%s]: ", pins[i].pin_name, pins[i].critical_role);

        if (!pull_present) {
            printf("[ПОМИЛКА] Пін висить у повітрі! Стан невизначений.\n");
            all_valid = false;
            continue;
        }

        if (actual_level_high == pins[i].required_level_high) {
            printf("[OK] Рівень відповідає режиму Normal Boot (%s)\n",
                   actual_level_high ? "HIGH" : "LOW");
        } else {
            printf("[КРИТИЧНО] Невідповідність! Очікується %s, підтягнуто до %s\n",
                   pins[i].required_level_high ? "HIGH" : "LOW",
                   actual_level_high ? "VCC" : "GND");
            all_valid = false;
        }
    }
    return all_valid;
}

int main(void) {
    StrappingPinConfig esp32_config[] = {
        {"GPIO0",  PULL_UP_VCC,   true,  "Flash Boot Mode"},
        {"GPIO2",  PULL_DOWN_GND, false, "Download Boot Mode Inhibitor"},
        {"GPIO12", PULL_DOWN_GND, false, "Flash Voltage 3.3V Selector"},
        {"GPIO15", PULL_UP_VCC,   true,  "Silent Boot Logging"}
    };

    size_t count = sizeof(esp32_config) / sizeof(esp32_config[0]);
    bool passed = audit_strapping_pins(esp32_config, count);

    printf("\nПідсумок аудиту: %s\n", passed ? "СХВАЛЕНО" : "ВІДХИЛЕНО");
    return passed ? 0 : 1;
}
