// MAVLink v2 повідомлення MANUAL_CONTROL (ID: #69) у типізованій структурі C++20
#include <cstdint>

namespace mavlink {

struct ManualControlMessage {
    int16_t pitch{0};        // Тангаж x: [-1000 .. 1000]
    int16_t roll{0};         // Крен y: [-1000 .. 1000]
    int16_t throttle{0};     // Тяга z: [0 .. 1000]
    int16_t yaw{0};          // Рискання r: [-1000 .. 1000]
    uint16_t buttons{0};     // Маска кнопок
    uint8_t target_system{0};// Ідентифікатор борту
};

} // namespace mavlink
