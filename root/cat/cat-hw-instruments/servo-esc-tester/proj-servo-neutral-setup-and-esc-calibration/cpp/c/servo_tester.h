#ifndef SERVO_TESTER_H
#define SERVO_TESTER_H

#include <stdint.h>
#include <stdbool.h>

/* Межеві значення ШІМ-імпульсу керування сервоприводами та ESC (мкс) */
#define SERVO_PWM_MIN_US        1000U   /* Крайнє ліве положення / 0% газу ESC */
#define SERVO_PWM_MAX_US        2000U   /* Крайнє праве положення / 100% газу ESC */
#define SERVO_PWM_NEUTRAL_US    1500U   /* Центральне положення нейтралі (1.5 мс) */
#define SERVO_PWM_PERIOD_US     20000U  /* Період повторення імпульсів (20 мс / 50 Гц) */

/* Параметри аналогово-цифрового перетворення */
#define SERVO_ADC_MAX_VALUE     4095U   /* Максимальне значення 12-бітного АЦП */

/* Параметри автосканування (Auto-sweep) */
#define SERVO_SWEEP_STEP_US     5U      /* Крок зміни ширини імпульсу на один ітераційний крок */
#define SERVO_SWEEP_INTERVAL_MS 10U     /* Інтервал між кроками автосканування (мс) */
#define SERVO_DEBOUNCE_MS       50U     /* Час антидребезгу кнопки (мс) */

/**
 * @brief Перелічення режимів роботи тестера.
 */
typedef enum {
    SERVO_MODE_MANUAL = 0, /* Ручне керування потенціометром через АЦП */
    SERVO_MODE_NEUTRAL,    /* Фіксована нейтраль (1500 мкс) */
    SERVO_MODE_AUTO_SWEEP  /* Автоматичне плавне сканування (1000–2000 мкс) */
} servo_mode_t;

/**
 * @brief Перелічення станів калібрування регулятора ходу (ESC).
 */
typedef enum {
    ESC_CALIB_IDLE = 0,       /* Калібрування не активне */
    ESC_CALIB_MAX_THROTTLE,   /* Подача максимального газу (2000 мкс) для зчитування точки 100% */
    ESC_CALIB_MIN_THROTTLE,   /* Подача мінімального газу (1000 мкс) для фіксації нуля */
    ESC_CALIB_COMPLETED       /* Калібрування завершено успішно */
} esc_calib_state_t;

/**
 * @brief Структура стану тестера сервоприводів та ESC.
 */
typedef struct {
    servo_mode_t mode;           /* Поточний режим роботи тестера */
    uint16_t current_pulse_us;   /* Поточна ширина імпульсу ШІМ у мікросекундах */
    int8_t sweep_dir;            /* Напрямок автосканування (+1 або -1) */
    uint32_t last_sweep_ms;      /* Таймштамп останньої зміни ширини в режимі Auto-sweep */
    bool last_button_state;      /* Попередній зчитаний стан кнопки перемикання */
    uint32_t button_debounce_ms; /* Таймштамп останньої зміни стану кнопки */
    esc_calib_state_t calib_state;/* Стан автомата калібрування ESC */
    uint32_t calib_timer_ms;     /* Лічильник затримок режимів калібрування ESC */
} servo_tester_t;

/**
 * @brief Ініціалізація структури стану тестера сервоприводів.
 * @param tester Вказівник на структуру тестера.
 */
void servo_tester_init(servo_tester_t *tester);

/**
 * @brief Перерахунок значення АЦП у тривалість імпульсу ШІМ (1000–2000 мкс).
 * @param adc_val Сире значення АЦП (0..4095).
 * @return Обчислена тривалість імпульсу в мікросекундах.
 */
uint16_t servo_tester_adc_to_pulse(uint16_t adc_val);

/**
 * @brief Встановлення режиму роботи тестера.
 * @param tester Вказівник на структуру тестера.
 * @param mode Новий режим роботи.
 */
void servo_tester_set_mode(servo_tester_t *tester, servo_mode_t mode);

/**
 * @brief Оновлення стану в ручному режимі (Manual).
 * @param tester Вказівник на структуру тестера.
 * @param adc_val Поточне значення АЦП потенціометра.
 */
void servo_tester_update_manual(servo_tester_t *tester, uint16_t adc_val);

/**
 * @brief Оновлення стану в режимі автоматичного свипу (Auto-sweep).
 * @param tester Вказівник на структуру тестера.
 * @param current_ms Поточний час системи у мілісекундах.
 */
void servo_tester_update_sweep(servo_tester_t *tester, uint32_t current_ms);

/**
 * @brief Обробка стану кнопки перемикання режимів із фільтрацією дребезгу.
 * @param tester Вказівник на структуру тестера.
 * @param raw_button_state Поточне фізичне значення кнопки (true = натиснута).
 * @param current_ms Поточний системний час у мілісекундах.
 */
void servo_tester_process_button(servo_tester_t *tester, bool raw_button_state, uint32_t current_ms);

/**
 * @brief Запуск процедури калібрування діапазону газу регулятора ESC.
 * @param tester Вказівник на структуру тестера.
 * @param current_ms Поточний системний час у мілісекундах.
 */
void servo_tester_start_esc_calibration(servo_tester_t *tester, uint32_t current_ms);

/**
 * @brief Періодична обробка кроків калібрування ESC.
 * @param tester Вказівник на структуру тестера.
 * @param current_ms Поточний системний час у мілісекундах.
 */
void servo_tester_update_esc_calibration(servo_tester_t *tester, uint32_t current_ms);

#endif /* SERVO_TESTER_H */
