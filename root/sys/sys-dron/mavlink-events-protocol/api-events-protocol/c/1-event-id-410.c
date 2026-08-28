#include <stdint.h>

// Оголошення структури кадру EVENT (MAVLink v2 ID 410)
#pragma pack(push, 1)
typedef struct {
    uint32_t id;                    // 32-бітний ідентифікатор події
    uint32_t event_time_boot_ms;    // Часова мітка від старту (мс)
    uint16_t sequence;              // Порядковий номер у черзі
    uint8_t  destination_component; // Цільовий вузол (0 = broadcast)
    uint8_t  destination_system;    // Цільова система (0 = broadcast)
    uint8_t  log_levels;            // Бітова маска рівнів важливості
    uint8_t  arguments[40];         // Двійковий буфер аргументів
} mavlink_event_t;
#pragma pack(pop)
