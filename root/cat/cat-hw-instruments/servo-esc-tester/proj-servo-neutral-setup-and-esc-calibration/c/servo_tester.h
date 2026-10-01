#ifndef SERVO_TESTER_H
#define SERVO_TESTER_H

#include <stdint.h>
#include <stdbool.h>

// Режими роботи тестера сервоприводів та регуляторів ходу (ESC)
typedef enum {
    SERVO_MODE_MANUAL = 0, // Ручне керування від потенціометра
    SERVO_MODE_NEUTRAL = 1, // Фіксоване центральне положення (1500 мкс)
    SERVO_MODE_SWEEP = 2   // Автоматичне циклічне сканування (1000..2000 мкс)
} servo_tester_mode_t;

// Структура стану тестера сервоприводів
typedef struct {
    servo_tester_mode_t mode; // Поточний режим роботи
    uint16_t pulse_width_us;   // Поточна ширина імпульсу у мікросекундах (1000..2000)
    int8_t sweep_dir;          // Напрямок сканування в режимі Auto-sweep (+1 або -1)
    uint32_t last_sweep_ms;    // Час останнього кроку сканування (мс)
    uint32_t last_button_ms;   // Час останнього змінення стану кнопки для дебаунсу (мс)
    bool last_button_state;    // Попередній зчитаний стан кнопки
    bool esc_calibrated;       // Прапор успішного проходження калібрування ESC
} servo_tester_t;

// Ініціалізація структури стану тестера
void servo_tester_init(servo_tester_t *tester);

// Ініціалізація периферійних модулів (ШІМ-таймер, АЦП, кнопки)
void servo_tester_hw_init(void);

// Встановлення тривалості імпульсу ШІМ (1000..2000 мкс) з обмеженням крайових значень
void servo_tester_set_pulse_us(servo_tester_t *tester, uint16_t pulse_us);

// Зчитування значення потенціометра через АЦП (повертає значення 1000..2000 мкс)
uint16_t servo_tester_read_adc_pulse(void);

// Перемикання режиму роботи на наступний по колу (Manual -> Neutral -> Sweep -> Manual)
void servo_tester_next_mode(servo_tester_t *tester);

// Оновлення стану тестера в неблокувальному головному циклі
void servo_tester_update(servo_tester_t *tester, uint32_t current_ms, bool button_pressed);

// Послідовна процедура безпечного калібрування діапазону газу для регуляторів ESC
void servo_tester_calibrate_esc(servo_tester_t *tester);

#endif // SERVO_TESTER_H
