#ifndef SERVO_TESTER_H
#define SERVO_TESTER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file servo_tester.h
 * @brief Модуль формування ШІМ-сигналу 50 Гц для драйверів AA5188 / KC0032.
 *
 * Спеціалізовані мікросхеми серводрайверів AA5188 та KC0032 очікують
 * стандартний сигнал керування з періодом 20 мс (50 Гц) та тривалістю
 * імпульсу 1000–2000 мкс (1.0–2.0 мс). Внутрішній компаратор аналогової
 * мікросхеми порівнює цей імпульс з імпульсом зворотного зв'язку потенціометра
 * та керує мостом Н для обертання двигуна.
 */

// Параметри керуючого сигналу ШІМ
#define SERVO_PWM_FREQ_HZ        50U      // Частота кадру ШІМ (50 Гц)
#define SERVO_PERIOD_US          20000U   // Період кадру (20 000 мкс = 20 мс)
#define SERVO_MIN_PULSE_US       1000U    // Мінімальний імпульс (0 градусів)
#define SERVO_NEUTRAL_PULSE_US   1500U    // Нейтральний імпульс (90 градусів)
#define SERVO_MAX_PULSE_US       2000U    // Максимальний імпульс (180 градусів)

#define SERVO_MIN_ANGLE_DEG      0U       // Мінімальний кут (градуси)
#define SERVO_MAX_ANGLE_DEG      180U     // Максимальний кут (градуси)

// Структура регістрів апаратного таймера мікроконтролера (симуляція HAL/Hardware)
typedef struct {
    volatile uint32_t CR1;   // Регістр керування (Control Register 1)
    volatile uint32_t PSC;   // Переддільник частоти (Prescaler)
    volatile uint32_t ARR;   // Регістр автоперезавантаження / період (Auto-Reload Register)
    volatile uint32_t CCR1;  // Регістр порівняння / тривалість імпульсу (Capture/Compare)
    volatile uint32_t CCER;  // Регістр дозволу виходу (Capture/Compare Enable)
} servo_timer_regs_t;

// Структура дескриптора сервотестера
typedef struct {
    servo_timer_regs_t *timer;  // Вказівник на регістри апаратного таймера
    uint32_t timer_clk_hz;      // Тактова частота таймера (Гц)
    uint16_t current_pulse_us;  // Поточна тривалість імпульсу в мкс
    bool is_active;             // Прапорець активності генератора ШІМ
} servo_tester_t;

/**
 * @brief Ініціалізація модуля сервотестера та апаратного таймера.
 * @param tester Вказівник на структуру сервотестера.
 * @param timer_hardware Вказівник на блок регістрів таймера.
 * @param system_clk_hz Частота тактування периферичного таймера (Гц).
 * @return true у разі успішної ініціалізації, false при невалідних параметрах.
 */
bool servo_tester_init(servo_tester_t *tester, servo_timer_regs_t *timer_hardware, uint32_t system_clk_hz);

/**
 * @brief Встановлення тривалості керуючого імпульсу в мікросекундах.
 * @param tester Вказівник на структуру сервотестера.
 * @param pulse_us Тривалість імпульсу (обмежується діапазоном 1000..2000 мкс).
 */
void servo_tester_set_pulse_us(servo_tester_t *tester, uint16_t pulse_us);

/**
 * @brief Встановлення позиції сервоприводу в градусах (0..180°).
 * @param tester Вказівник на структуру сервотестера.
 * @param angle_deg Кут повернення в градусах.
 */
void servo_tester_set_angle(servo_tester_t *tester, uint8_t angle_deg);

/**
 * @brief Отримання поточної тривалості імпульсу в мікросекундах.
 * @param tester Вказівник на структуру сервотестера.
 * @return Тривалість імпульсу в мкс.
 */
uint16_t servo_tester_get_pulse_us(const servo_tester_t *tester);

/**
 * @brief Отримання поточного встановленого кута в градусах.
 * @param tester Вказівник на структуру сервотестера.
 * @return Кут у градусах (0..180).
 */
uint8_t servo_tester_get_angle(const servo_tester_t *tester);

/**
 * @brief Запуск генерації ШІМ-сигналу для AA5188/KC0032.
 * @param tester Вказівник на структуру сервотестера.
 */
void servo_tester_start(servo_tester_t *tester);

/**
 * @brief Зупинка генерації ШІМ-сигналу.
 * @param tester Вказівник на структуру сервотестера.
 */
void servo_tester_stop(servo_tester_t *tester);

/**
 * @brief Виконання калібрування нейтралі (1500 мкс) для вистави потенціометра.
 * @param tester Вказівник на структуру сервотестера.
 */
void servo_tester_calibrate_neutral(servo_tester_t *tester);

#endif // SERVO_TESTER_H
