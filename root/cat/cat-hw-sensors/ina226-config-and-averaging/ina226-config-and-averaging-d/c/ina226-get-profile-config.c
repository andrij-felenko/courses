// Перемикання конфігураційних профілів INA226 залежно від стану системи
#include <stdint.h>

typedef enum {
    INA226_PROFILE_FAST_PROTECTION = 0, // 140 мкс, без усереднення (швидкий відгук)
    INA226_PROFILE_BALANCED        = 1, // 1.1 мс, 16 усереднень (стандартний моніторинг)
    INA226_PROFILE_PRECISION_LOG   = 2  // 8.244 мс, 512 усереднень (висока точність)
} ina226_profile_t;

// Словник конфігурацій за замовчуванням
static const uint16_t PROFILE_CONFIGS[] = {
    [INA226_PROFILE_FAST_PROTECTION] = (0x00u << 9) | (0x00u << 6) | (0x00u << 3) | 0x07u, // 0x0007
    [INA226_PROFILE_BALANCED]        = (0x02u << 9) | (0x04u << 6) | (0x04u << 3) | 0x07u, // 0x0497
    [INA226_PROFILE_PRECISION_LOG]   = (0x06u << 9) | (0x07u << 6) | (0x07u << 3) | 0x07u  // 0x0DF7
};

uint16_t ina226_get_profile_config(ina226_profile_t profile) {
    if (profile > INA226_PROFILE_PRECISION_LOG) {
        return PROFILE_CONFIGS[INA226_PROFILE_BALANCED];
    }
    return PROFILE_CONFIGS[profile];
}
