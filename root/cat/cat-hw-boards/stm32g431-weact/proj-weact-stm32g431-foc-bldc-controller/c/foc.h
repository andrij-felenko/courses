#ifndef FOC_H
#define FOC_H

#include <stdint.h>
#include <stdbool.h>

// Параметри дискретного ПІ-регулятора з анти-віндапом
typedef struct {
    float kp;       // Пропорційний коефіцієнт
    float ki;       // Інтегральний коефіцієнт
    float integral; // Сума накопиченого інтеграла
    float out_min;  // Мінімальне обмеження виходу
    float out_max;  // Максимальне обмеження виходу
} pi_controller_t;

// Внутрішній стан контролера FOC
typedef struct {
    // Виміряні фазні струми
    float i_a;
    float i_b;
    float i_c;

    // Струми у стаціонарній системі (Clarke)
    float i_alpha;
    float i_beta;

    // Струми у синхронній обертальній системі (Park)
    float i_d;
    float i_q;

    // Цільові струми
    float target_i_d;
    float target_i_q;

    // Цільова та виміряна швидкість обертання
    float target_speed;
    float measured_speed;

    // Поточний електричний кут ротора
    float electrical_angle;

    // Вихідні напруги ПІ-регуляторів
    float v_d;
    float v_q;

    // Напруги у нерухомій системі
    float v_alpha;
    float v_beta;

    // Розраховані значення каналів ШІМ (CCR1, CCR2, CCR3)
    uint16_t duty_a;
    uint16_t duty_b;
    uint16_t duty_c;

    // ПІ-регулятори струмів Id, Iq та швидкості
    pi_controller_t pi_d;
    pi_controller_t pi_q;
    pi_controller_t pi_speed;

    float    bus_voltage;
    uint16_t pwm_period;
} foc_state_t;

// Ініціалізація структури ПІ-регулятора
void pi_controller_init(pi_controller_t *pi, float kp, float ki, float out_min, float out_max);

// Оновлення ПІ-регулятора за шаг dt
float pi_controller_update(pi_controller_t *pi, float setpoint, float measured, float dt);

// Скидання інтегральної складової
void pi_controller_reset(pi_controller_t *pi);

// Ініціалізація алгоритму FOC
void foc_init(foc_state_t *foc, float bus_voltage, uint16_t pwm_period);

// Пряме перетворення Кларк
void foc_clarke_transform(float i_a, float i_b, float *i_alpha, float *i_beta);

// Пряме перетворення Парка
void foc_park_transform(float i_alpha, float i_beta, float cos_th, float sin_th, float *i_d, float *i_q);

// Зворотне перетворення Парка
void foc_inv_park_transform(float v_d, float v_q, float cos_th, float sin_th, float *v_alpha, float *v_beta);

// Векторна модуляція ШІМ (SVPWM)
void foc_svpwm(float v_alpha, float v_beta, float v_bus, uint16_t pwm_period, 
               uint16_t *duty_a, uint16_t *duty_b, uint16_t *duty_c);

// Виконання швидкодіючого контуру регулювання струму
void foc_update_current_loop(foc_state_t *foc, float dt);

// Виконання контуру регулювання швидкості
void foc_update_speed_loop(foc_state_t *foc, float dt);

#endif // FOC_H
