#include <cstdint>
#include <type_traits>

struct alignas(8) SensorPayload {
    uint8_t  sensor_id;   // 1 байт,  зміщення 0
    // 3 байти набивки (padding)
    uint32_t timestamp;   // 4 байти, зміщення 4
    double   temperature; // 8 байтів, зміщення 8
    uint8_t  status_flag; // 1 байт,  зміщення 16
    // 7 байтів кінцевої набивки
};

static_assert(sizeof(SensorPayload) == 24);
static_assert(alignof(SensorPayload) == 8);
