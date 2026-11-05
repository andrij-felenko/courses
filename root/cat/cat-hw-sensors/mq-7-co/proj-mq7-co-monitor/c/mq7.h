#ifndef MQ7_H
#define MQ7_H

#include <stdint.h>
#include <stdbool.h>

// Стани автомата нагрівання MQ-7
typedef enum {
    MQ7_STATE_INIT,
    MQ7_STATE_HEATING_HIGH, // Фаза очищення: 60 сек при 5.0V
    MQ7_STATE_HEATING_LOW   // Фаза вимірювання: 90 сек при 1.4V
} mq7_state_t;

// Структура для збереження контексту давача
typedef struct {
    mq7_state_t state;
    uint32_t timer_start;
    float ppm;
    bool alarm_active;
} mq7_sensor_t;

// Конфігураційні часові константи
#define MQ7_TIME_HIGH_MS 60000 // 60 секунд
#define MQ7_TIME_LOW_MS  90000 // 90 секунд

// Константи ШІМ (припускаємо 8-бітний таймер, 0-255)
#define MQ7_PWM_HIGH     255   // 100% шпаруватість для 5.0V
#define MQ7_PWM_LOW      71    // ~28% шпаруватість для 1.4V (255 * 1.4 / 5.0)

// Небезпечний поріг концентрації (приклад)
#define MQ7_ALARM_THRESHOLD_PPM 50.0f

// Інтерфейс
void mq7_init(mq7_sensor_t *sensor);
bool mq7_update(mq7_sensor_t *sensor);

// Функції, які мають бути реалізовані у платформозалежному коді
extern uint32_t hal_get_time_ms(void);
extern void hal_pwm_set_duty(uint8_t duty);
extern uint16_t hal_adc_read(void);
extern void hal_buzzer_set(bool state);

#endif // MQ7_H
