#include <cstdint>

namespace autopilot::failsafe {

struct TelemetryFrame {
    uint64_t timestamp_us{0};       // Час польотного контролера (мікросекунди)
    uint32_t active_faults_mask{0}; // Бітова маска поточних підтверджених відмов
    uint8_t  active_action{0};      // Поточний аварійний режим (0=None, 1=Warn, 2=AltHold, 3=RTL, 4=Land, 5=Term)
    uint8_t  executing_arbiter{0};  // Ідентифікатор правила, що згенерувало дію
    uint16_t rc_valid_frames_sec{0};// Лічильник валідних RC-пакетів за останню секунду
    float    gnss_hdop{0.0f};       // Поточний HDOP супутникового приймача
    float    batt_cell_min_v{0.0f}; // Мінімальна напруга серед усіх комірок батареї
    float    distance_to_fence_m{0.0f}; // Відстань до найближчого кордону геозони
};

} // namespace autopilot::failsafe
