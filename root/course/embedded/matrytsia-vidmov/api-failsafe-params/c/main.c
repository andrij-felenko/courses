#include <stdint.h>

typedef struct {
    uint64_t timestamp_us;       // Час польотного контролера (мікросекунди)
    uint32_t active_faults_mask; // Бітова маска поточних підтверджених відмов
    uint8_t  active_action;      // Поточний аварійний режим (0=None, 1=Warn, 2=AltHold, 3=RTL, 4=Land, 5=Term)
    uint8_t  executing_arbiter;  // Ідентифікатор правила, що згенерувало дію
    uint16_t rc_valid_frames_sec;// Лічильник валідних RC-пакетів за останню секунду
    float    gnss_hdop;          // Поточний HDOP супутникового приймача
    float    batt_cell_min_v;    // Мінімальна напруга серед усіх комірок батареї
    float    distance_to_fence_m;// Відстань до найближчого кордону геозони
} failsafe_telemetry_t;
