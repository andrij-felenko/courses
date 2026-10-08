#include <stdint.h>

typedef struct {
    uint16_t u_idle_mv;     // Напруга холостого ходу в мілівольтах
    uint16_t u_load_mv;     // Напруга під навантаженням в мілівольтах
    uint16_t u_cutoff_mv;   // Порогова напруга відсічки в мілівольтах
    uint16_t r_tip_moxm;    // Опір жала в міліомах (наприклад, 8000 мОм = 8.0 Ом)
} power_metrics_t;

// Обчислення максимального заповнення ШІМ (0..255) для запобігання просіданню живлення
uint8_t calculate_max_pwm_limit(const power_metrics_t* metrics) {
    if (metrics->u_load_mv >= metrics->u_idle_mv || metrics->u_load_mv <= metrics->u_cutoff_mv) {
        return 255; // Якщо дані некоректні або напруга вже нижче порогу, межу не змінюємо
    }

    // Обчислення спаду напруги та струму навантаження
    uint32_t delta_u_mv = metrics->u_idle_mv - metrics->u_load_mv;
    uint32_t current_ma = ((uint32_t)metrics->u_load_mv * 1000) / metrics->r_tip_moxm;
    
    if (current_ma == 0) return 255;
    
    // Внутрішній опір джерела у міліомах: R_src = Delta_U / I
    uint32_t r_src_moxm = (delta_u_mv * 1000) / current_ma;

    // Розрахунок граничного заповнення ШІМ D_max
    uint32_t allowed_drop_mv = metrics->u_idle_mv - metrics->u_cutoff_mv;
    uint32_t max_pwm = (allowed_drop_mv * metrics->r_tip_moxm * 255) / 
                       ((uint32_t)metrics->u_cutoff_mv * r_src_moxm);

    if (max_pwm > 255) return 255;
    return (uint8_t)max_pwm;
}
