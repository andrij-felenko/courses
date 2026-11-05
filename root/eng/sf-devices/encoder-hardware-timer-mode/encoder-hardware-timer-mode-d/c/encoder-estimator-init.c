#include <stdint.h>
#include <math.h>

#define M_PI_F 3.14159265358979323846f

typedef struct {
    int64_t  total_ticks;       // Розширений 64-бітний лічильник
    uint32_t cpr;               // Кількість відліків на оберт (x4 CPR)
    float    wheel_radius_m;    // Радіус колеса в метрах
    float    filter_alpha;      // Коефіцієнт ФНЧ швидкості (0..1)
    float    filtered_velocity; // Фільтрована кутова швидкість (рад/с)
    int64_t  prev_ticks;        // Попереднє значення дискрет
} EncoderEstimator;

void encoder_estimator_init(EncoderEstimator *est, uint32_t cpr, float wheel_radius_m, float filter_alpha) {
    est->total_ticks = 0;
    est->cpr = cpr;
    est->wheel_radius_m = wheel_radius_m;
    est->filter_alpha = filter_alpha;
    est->filtered_velocity = 0.0f;
    est->prev_ticks = 0;
}

// Розрахунок позиції в радіанах
float encoder_get_angle_rad(const EncoderEstimator *est) {
    return (2.0f * M_PI_F * (float)est->total_ticks) / (float)est->cpr;
}

// Розрахунок лінійного переміщення в метрах
float encoder_get_linear_distance_m(const EncoderEstimator *est) {
    return encoder_get_angle_rad(est) * est->wheel_radius_m;
}

// Періодичне оновлення швидкості (викликається в перериванні таймера з періодом dt_sec)
void encoder_estimator_update(EncoderEstimator *est, int64_t current_ticks, float dt_sec) {
    est->total_ticks = current_ticks;
    int64_t delta_ticks = current_ticks - est->prev_ticks;
    est->prev_ticks = current_ticks;

    // Кутове переміщення за крок dt
    float delta_angle = (2.0f * M_PI_F * (float)delta_ticks) / (float)est->cpr;
    
    // Сира швидкість (рад/с)
    float raw_velocity = delta_angle / dt_sec;

    // Фільтрація першого порядку (ФНЧ)
    est->filtered_velocity = (est->filter_alpha * raw_velocity) + 
                             ((1.0f - est->filter_alpha) * est->filtered_velocity);
}
