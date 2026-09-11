#include <stdint.h>
#include <stdbool.h>

// Стани кінцевого автомата приводу
typedef enum {
    MOTOR_STATE_COAST = 0,   // Вільний вибіг (Hi-Z, обмотка розімкнена)
    MOTOR_STATE_FORWARD,     // Обертання вперед
    MOTOR_STATE_REVERSE,     // Обертання назад
    MOTOR_STATE_BRAKE,       // Динамічне гальмування (обмотка закорочена)
    MOTOR_STATE_FAULT        // Аварійне блокування (перевантаження за струмом)
} motor_state_t;

// Статуси виконання операцій API
typedef enum {
    MOTOR_OK = 0,            // Операцію виконано успішно
    MOTOR_ERR_INVALID_ARG,   // Неприпустиме значення параметра
    MOTOR_ERR_FAULT_ACTIVE,  // Команду відхилено: активний аварійний стан
    MOTOR_ERR_HW_FAILURE     // Збій апаратної периферії таймера чи АЦП
} motor_status_t;

// Статична конфігурація апаратної прив'язки та обмежень безпеки
typedef struct {
    uint8_t pin_in1;             // Цифровий вивід керування першим плечем моста
    uint8_t pin_in2;             // Цифровий вивід керування другим плечем моста
    uint8_t pin_pwm;             // Вивід апаратного ШІМ
    uint8_t pin_current_sense;   // Аналоговий вивід датчика струму (АЦП)
    uint32_t pwm_frequency_hz;   // Робоча частота ШІМ, Гц

    uint16_t dead_time_us;       // Пауза мертвого часу між перемиканнями, мкс
    float slew_rate_limit;       // Максимальна зміна швидкості на секунду, частка/с
    uint16_t stall_current_ma;   // Поріг струму заклинювання ротора, мА
    uint16_t stall_blanking_ms;  // Тривалість ігнорування пускового струму, мс
    uint16_t stall_timeout_ms;   // Допустимий час перевантаження до аварії, мс
} motor_config_t;

// Дескриптор робочого стану екземпляра приводу
typedef struct {
    motor_config_t config;       // Копія конфігураційних параметрів
    motor_state_t state;         // Поточний стан кінцевого автомата
    float target_speed;          // Задана нормалізована швидкість [-1.0f .. +1.0f]
    float current_speed;         // Фактична згладжена швидкість після темпування
    uint16_t measured_current_ma;// Останнє виміряне значення струму якоря, мА
    uint32_t stall_timer_ms;     // Лічильник часу роботи з перевантаженням за струмом
    uint32_t last_update_ms;     // Позначка системного часу останнього розрахунку
    uint32_t fault_flags;        // Бітова маска джерел виникнення аварії
} motor_t;

// Прототипи функцій інтерфейсу керування
motor_status_t motor_init(motor_t *motor, const motor_config_t *config);
motor_status_t motor_set_speed(motor_t *motor, float speed);
motor_status_t motor_brake(motor_t *motor);
motor_status_t motor_coast(motor_t *motor);
motor_status_t motor_reset_fault(motor_t *motor);
motor_status_t motor_update(motor_t *motor, uint32_t delta_time_ms);
