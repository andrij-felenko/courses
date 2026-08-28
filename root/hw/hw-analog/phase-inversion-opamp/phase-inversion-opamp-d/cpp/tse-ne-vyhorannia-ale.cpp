// Чи безпечний синфазний рівень для ОП на одному живленні 0..5 В?
// Вікно з довідника: [v_cm_min .. v_cm_max]. Сигнал може мати викид.
#include <stdbool.h>

static const float V_CM_MIN = 0.0f;     // нижня межа синфазного вікна, В
static const float V_CM_MAX = 3.5f;     // верхня межа: V+ − 1.5 В
static const float MARGIN   = 0.20f;    // запас на дрейф/температуру, В

bool cm_level_safe(float v_signal_peak) {
    float lo = V_CM_MIN + MARGIN;       // 0.20 В
    float hi = V_CM_MAX - MARGIN;       // 3.30 В
    return (v_signal_peak >= lo) && (v_signal_peak <= hi);
}

// приклад: давач інколи викидає до 3.8 В
//   cm_level_safe(3.8f) → 3.8 > 3.30 → false → переворот можливий!
