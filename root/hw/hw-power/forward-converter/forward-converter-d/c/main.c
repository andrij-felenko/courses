#include <stdint.h>
#include <stdbool.h>

// Розрахунок максимальної шпаруватості та перевірка безпеки розмагнічування
typedef struct {
    float vin;
    float vout;
    float np_ns_ratio;
    float np_nr_ratio;
    float duty_limit;
} ForwardParams;

// Обчислення безпечної шпаруватості ШІМ
float forward_calculate_duty(const ForwardParams* p) {
    // Теоретична межа за вольт-секундним балансом
    float d_max_theoretical = 1.0f / (1.0f + p->np_nr_ratio);
    
    // Захисний інженерний бар'єр (віднімаємо 5% для гарантованого скидання)
    float d_safe_ceiling = d_max_theoretical - 0.05f;
    if (d_safe_ceiling > p->duty_limit) {
        d_safe_ceiling = p->duty_limit;
    }
    
    // Розрахунок необхідної шпаруватості для підтримки Vout
    float d_target = (p->vout / p->vin) * p->np_ns_ratio;
    
    // Захисне насичення
    if (d_target > d_safe_ceiling) {
        return d_safe_ceiling;
    }
    if (d_target < 0.05f) {
        return 0.05f;
    }
    return d_target;
}
