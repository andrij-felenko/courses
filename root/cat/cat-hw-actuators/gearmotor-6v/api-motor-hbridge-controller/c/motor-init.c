#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Коди завершення операцій драйвера мотора
typedef enum {
    MOTOR_OK = 0,               // Операцію виконано успішно
    MOTOR_ERR_NULL_PTR = -1,     // Передано нульовий вказівник на структуру
    MOTOR_ERR_INVALID_PIN = -2,  // Помилка конфігурації ліній вводу-виводу
    MOTOR_ERR_PWM_FAIL = -3,     // Помилка налаштування таймера або частоти ШІМ
    MOTOR_ERR_INVALID_PARAM = -4 // Параметри виходять за допустимі межі
} motor_status_t;

// Режими зупинки вихідного вала
typedef enum {
    MOTOR_STOP_COAST = 0,        // Вільний вибіг у високоімпедансному стані (Hi-Z)
    MOTOR_STOP_BRAKE = 1         // Динамічне гальмування закороченням обмотки на землю
} motor_stop_mode_t;

// Стани кінцевого автомата приводу
typedef enum {
    MOTOR_STATE_UNINITIALIZED = 0, // Периферію не налаштовано, запуск заборонено
    MOTOR_STATE_IDLE,              // Драйвер налаштовано, ключі знеструмлені
    MOTOR_STATE_RUNNING,           // Вал обертається, активна генерація ШІМ
    MOTOR_STATE_FAULT              // Аварійне блокування живлення
} motor_state_t;

// Налаштування екземпляра приводу
typedef struct {
    uint16_t pin_in1;            // Номер виводу першого напівмоста
    uint16_t pin_in2;            // Номер виводу другого напівмоста
    void *port_in1;              // Вказівник на апаратний GPIO-порт виводу IN1
    void *port_in2;              // Вказівник на апаратний GPIO-порт виводу IN2
    
    uint32_t pwm_frequency_hz;   // Цільова частота ШІМ (20000 Гц)
    uint32_t timer_clock_hz;     // Тактова частота шини таймера мікроконтролера
    
    float deadband_cutoff;       // Поріг відсікання шуму навколо нуля (0.02..0.05)
    float deadband_min_duty;     // Мінімальна шпаруватість рушання редуктора (0.15..0.22)
} motor_config_t;

// Робочий дескриптор екземпляра мотора
typedef struct {
    motor_config_t config;       // Збережена робоча конфігурація
    motor_state_t state;         // Поточний стан автомата приводу
    float current_speed;         // Поточна нормалізована швидкість [-1.0 .. +1.0]
    float current_duty;          // Поточна шпаруватість таймера [0.0 .. 1.0]
    uint32_t timer_arr;          // Розрахований період таймера (регістр ARR)
} motor_t;

// Низькорівневі прототипи платформно-залежних викликів
void platform_gpio_write(void *port, uint16_t pin, bool level);
void platform_pwm_set_duty(void *port, uint16_t pin, uint32_t compare_value);

motor_status_t motor_init(motor_t *motor, const motor_config_t *config)
{
    if (motor == NULL || config == NULL) {
        return MOTOR_ERR_NULL_PTR;
    }

    // Перевірка коректності призначення виводів керування
    if (config->port_in1 == NULL || config->port_in2 == NULL) {
        return MOTOR_ERR_INVALID_PIN;
    }
    if (config->port_in1 == config->port_in2 && config->pin_in1 == config->pin_in2) {
        return MOTOR_ERR_INVALID_PIN;
    }

    // Перевірка допустимого діапазону частоти ШІМ
    if (config->pwm_frequency_hz < 1000 || config->pwm_frequency_hz > 50000) {
        return MOTOR_ERR_PWM_FAIL;
    }
    if (config->timer_clock_hz == 0) {
        return MOTOR_ERR_PWM_FAIL;
    }

    // Розрахунок періоду лічильника: ARR = (f_timer / f_pwm) - 1
    uint32_t calculated_arr = (config->timer_clock_hz / config->pwm_frequency_hz) - 1;
    
    // Перевірка достатності роздільної здатності регулювання
    if (calculated_arr < 200 || calculated_arr > 0xFFFF) {
        return MOTOR_ERR_PWM_FAIL;
    }

    // Перевірка меж компенсації зони нечутливості
    if (config->deadband_cutoff < 0.0f || config->deadband_cutoff >= 0.2f ||
        config->deadband_min_duty < 0.0f || config->deadband_min_duty >= 0.5f ||
        config->deadband_cutoff >= config->deadband_min_duty) {
        return MOTOR_ERR_INVALID_PARAM;
    }

    motor->config = *config;
    motor->timer_arr = calculated_arr;
    motor->current_speed = 0.0f;
    motor->current_duty = 0.0f;

    // Апаратне переведення виводів моста у стан вибігу (COAST)
    platform_gpio_write(motor->config.port_in1, motor->config.pin_in1, false);
    platform_gpio_write(motor->config.port_in2, motor->config.pin_in2, false);
    platform_pwm_set_duty(motor->config.port_in1, motor->config.pin_in1, 0);
    platform_pwm_set_duty(motor->config.port_in2, motor->config.pin_in2, 0);

    motor->state = MOTOR_STATE_IDLE;
    return MOTOR_OK;
}
