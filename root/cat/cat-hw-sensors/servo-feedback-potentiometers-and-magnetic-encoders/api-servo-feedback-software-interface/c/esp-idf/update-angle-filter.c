#include <math.h>
#include <stdint.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    float filtered_angle_raw;
    float alpha; // Коефіцієнт згладжування (0.0 < alpha <= 1.0)
    uint16_t max_res;
    bool initialized;
} angle_filter_t;

float update_angle_filter(angle_filter_t *f, uint16_t new_raw_angle) {
    if (!f->initialized) {
        f->filtered_angle_raw = (float)new_raw_angle;
        f->initialized = true;
    } else {
        float delta = (float)new_raw_angle - f->filtered_angle_raw;
        float half_res = f->max_res / 2.0f;
        
        // Корекція переходу через кордон розрядності (360 -> 0 або 0 -> 360)
        if (delta > half_res) {
            delta -= f->max_res;
        } else if (delta < -half_res) {
            delta += f->max_res;
        }
        
        f->filtered_angle_raw += f->alpha * delta;
        
        // Нормалізація в межах 0..max_res
        if (f->filtered_angle_raw >= f->max_res) {
            f->filtered_angle_raw -= f->max_res;
        } else if (f->filtered_angle_raw < 0.0f) {
            f->filtered_angle_raw += f->max_res;
        }
    }
    
    // Перетворення у радіани
    return (f->filtered_angle_raw * 2.0f * (float)M_PI) / (float)f->max_res;
}
