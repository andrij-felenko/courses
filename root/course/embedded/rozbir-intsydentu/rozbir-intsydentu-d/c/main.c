#include <stdbool.h>
#include <stdint.h>
#include <math.h>

typedef enum {
    FAULT_NONE = 0,
    FAULT_ACTUATOR_SATURATION,
    FAULT_MAG_FIELD_DISTORTION,
    FAULT_BATTERY_COLLAPSE
} CrashFault;

// Аналіз кадру польотних даних
CrashFault evaluate_frame(float roll_err_deg, float m1_cmd, float m2_cmd, 
                          float mag_innov, float current_a, float voltage_v) {
    // 1. Просадка батареї нижче критичної відсічки
    if (voltage_v < 13.0f && current_a > 30.0f) {
        return FAULT_BATTERY_COLLAPSE;
    }
    // 2. Втрата мотора: максимальна асиметрія при зростанні помилки
    if (m1_cmd > 0.98f && m2_cmd < 0.05f && fabsf(roll_err_deg) > 20.0f) {
        return FAULT_ACTUATOR_SATURATION;
    }
    // 3. Магнітна завада: стрибок нев'язки пропорційно до струму
    if (mag_innov > 0.5f && current_a > 35.0f) {
        return FAULT_MAG_FIELD_DISTORTION;
    }
    return FAULT_NONE;
}
