#ifndef MCU_PERIPH_H
#define MCU_PERIPH_H

#include <stdint.h>
#include <stdbool.h>

// Структура налаштування аналогової та цифрової периферії STM32G431
typedef struct {
    uint32_t pwm_frequency_hz;   // Частота ШІМ таймера TIM1 (Гц)
    uint16_t dead_time_ns;       // Мертвий час для комплементарних каналів (нс)
    float    shunt_resistor_ohm; // Опір токовимірювальних шунтів (Ом)
    float    opamp_gain;         // Підсилення OPAMP у режимі PGA
    float    adc_vref;           // Опорна напруга аналогово-цифрового перетворювача (В)
} mcu_periph_config_t;

// Виміряні струми фаз BLDC-двигуна
typedef struct {
    float i_a; // Струм фази A (Ампери)
    float i_b; // Струм фази B (Ампери)
    float i_c; // Струм фази C (Ампери)
} phase_currents_t;

// Ініціалізація периферійних модулів: TIM1, OPAMP1/2, ADC1/2, CORDIC
bool mcu_periph_init(const mcu_periph_config_t *config);

// Ввімкнення та вимкнення силових каналів ШІМ (перемикання BDTR_MOE)
void mcu_periph_enable_pwm(bool enable);

// Запис порівняльних значень ШІМ у регістри TIM1->CCR1, CCR2, CCR3
void mcu_periph_set_duty_cycles(uint16_t duty_a, uint16_t duty_b, uint16_t duty_c);

// Зчитування миттєвих фазних струмів з АЦП
void mcu_periph_read_phase_currents(phase_currents_t *currents);

// Отримання максимального значення лічильника TIM1 (ARR)
uint16_t mcu_periph_get_pwm_period(void);

// Розрахунок косинуса та синуса за допомогою апаратного співпроцесора CORDIC
void mcu_periph_cordic_cos_sin(float angle_rad, float *out_cos, float *out_sin);

// Процедура калібрування нульового зсуву операційних підсилювачів та АЦП
void mcu_periph_calibrate_current_offsets(void);

#endif // MCU_PERIPH_H
