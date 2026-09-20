#include <stdbool.h>
#include <math.h>

#define RVDT_SUM_MIN_VOLTS  0.1f   // Мінімальна сумарна напруга обмоток (В)
#define RVDT_SCALE_RAD      0.7853f // Масштабний коефіцієнт (рад)

typedef struct {
    float v_s1;          // Амплітуда першої вторинної обмотки (В)
    float v_s2;          // Амплітуда другої вторинної обмотки (В)
    float raw_angle_rad; // Обчислений сирий кут (рад)
} rvdt_ratiometric_t;

bool rvdt_calculate_ratiometric_angle(rvdt_ratiometric_t *rvdt) {
    if (rvdt == NULL) {
        return false;
    }
    
    float sum = rvdt->v_s1 + rvdt->v_s2;
    if (sum < RVDT_SUM_MIN_VOLTS) {
        // Помилка: обрив обмотки або втрата збудження
        return false;
    }
    
    float diff = rvdt->v_s1 - rvdt->v_s2;
    float m_raw = diff / sum;
    rvdt->raw_angle_rad = m_raw * RVDT_SCALE_RAD;
    return true;
}
