#include <math.h>

typedef struct {
    float theta_hat;  /* Оцінка кута в радіанах */
    float omega_hat;  /* Оцінка кутової швидкості в рад/с */
    float v_i;        /* Стан інтегратора регулятора */
    float K_p;        /* Пропорційний коефіцієнт */
    float K_i;        /* Інтегральний коефіцієнт */
    float Ts;         /* Період дискретизації в секундах */
} RDC_TrackingLoop;

void rdc_update(RDC_TrackingLoop *rdc, float v_sin, float v_cos) {
    /* Обчислення сигналу тригонометричної неузгодженості */
    float e = v_sin * cosf(rdc->theta_hat) - v_cos * sinf(rdc->theta_hat);
    
    /* Оновлення інтегратора контуру */
    rdc->v_i += rdc->K_i * rdc->Ts * e;
    
    /* Оцінка кутової швидкості */
    rdc->omega_hat = rdc->K_p * e + rdc->v_i;
    
    /* Інтегрування швидкості для отримання нової оцінки кута */
    rdc->theta_hat += rdc->Ts * rdc->omega_hat;
    
    /* Нормалізація кута в межах від 0 до 2*PI */
    if (rdc->theta_hat >= 2.0f * (float)M_PI) {
        rdc->theta_hat -= 2.0f * (float)M_PI;
    } else if (rdc->theta_hat < 0.0f) {
        rdc->theta_hat += 2.0f * (float)M_PI;
    }
}
