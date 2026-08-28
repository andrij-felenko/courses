#include <cstdint>

enum StatusFlags : uint8_t {
    FLAG_INVALID = 0,
    FLAG_VALID   = 1 << 0,
    FLAG_CALIB   = 1 << 1
};

struct TelemetryRecord {
    uint32_t sensor_id;     // Ідентифікатор датчика (4 байти)
    uint64_t timestamp_ns;  // Мітка часу в наносекундах (8 байтів)
    float    raw_value;     // Фізичне виміряне значення (4 байти)
    uint8_t  flags;         // Прапорці стану (1 байт)
};
