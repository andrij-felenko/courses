#ifndef ESC_CONTROL_H
#define ESC_CONTROL_H

#include <stdint.h>
#include <stdbool.h>

/* Часові параметри ШІМ-сигналу керування ESC (у мікросекундах) */
#define ESC_PWM_MIN_US         1000U   /* 0% дроселя (мінімальний імпульс / стоп) */
#define ESC_PWM_MAX_US         2000U   /* 100% дроселя (максимальний імпульс) */
#define ESC_PWM_NEUTRAL_US     1000U   /* Початковий безпечний імпульс армування */
#define ESC_PWM_FREQ_HZ        50U     /* Стандартна частота ШІМ для серво/ESC (50 Гц = 20 мс) */
#define ESC_PWM_PERIOD_US      20000U  /* Період таймера ШІМ у мікросекундах (20 000 мкс) */

/* Параметри вимірювання напруги лінії BEC (Battery Eliminator Circuit) */
#define BEC_VREF_VOLTS         3.3f    /* Опорна напруга АЦП мікроконтролера (В) */
#define BEC_ADC_MAX_VALUE      4095.0f /* Максимальне значення 12-бітного АЦП (2^12 - 1) */

/* Коефіцієнт резистивного дільника напруги (R1 = 10кОм, R2 = 10кОм) */
#define BEC_R1_OHMS            10000.0f
#define BEC_R2_OHMS            10000.0f
#define BEC_DIVIDER_RATIO      ((BEC_R1_OHMS + BEC_R2_OHMS) / BEC_R2_OHMS) /* = 2.0 */

/* Граничні значення напруги BEC (номінал 5.0 В) */
#define BEC_VOLTAGE_NOMINAL    5.00f   /* Номінальна напруга 5В */
#define BEC_VOLTAGE_WARN       4.75f   /* Попередження про просідання живлення */
#define BEC_VOLTAGE_CRIT       4.50f   /* Критичне значення (відключення дроселя для захисту) */

/**
 * @brief Перелічення станів напруги лінії BEC.
 */
typedef enum {
    BEC_STATUS_OK = 0,     /* Напруга в межах норми (>= 4.75 В) */
    BEC_STATUS_WARNING,    /* Легке просідання напруги (4.50 В .. 4.75 В) */
    BEC_STATUS_CRITICAL    /* Небезпечне просідання напруги (< 4.50 В) */
} bec_status_t;

/**
 * @brief Структура стану драйвера керування ESC BLHeli та моніторингу BEC.
 */
typedef struct {
    uint16_t current_pulse_us; /* Поточна ширина імпульсу ШІМ (мкс) */
    float bec_voltage;         /* Обчислена поточна напруга BEC (В) */
    bec_status_t status;       /* Поточний стан лінійки живлення BEC */
    bool is_armed;             /* Прапорець завершення процедури армування ESC */
    bool emergency_stop;       /* Прапорець аварійного блокування через низьку напругу */
} esc_driver_t;

/**
 * @brief Ініціалізація периферії мікроконтролера (таймер ШІМ, АЦП) та структури драйвера.
 * @param driver Вказівник на структуру стану драйвера ESC.
 */
void esc_init(esc_driver_t *driver);

/**
 * @brief Задання тривалості керуючого імпульсу дроселювання.
 * @param driver Вказівник на структуру драйвера ESC.
 * @param pulse_us Бажана тривалість імпульсу в мікросекундах (1000–2000 мкс).
 */
void esc_set_throttle(esc_driver_t *driver, uint16_t pulse_us);

/**
 * @brief Математичний перерахунок сирого значення АЦП у напругу лінії BEC (у вольтах).
 * @param raw_adc Сире значення з регістру АЦП (0..4095).
 * @return float Виміряна напруга лінії BEC у вольтах.
 */
float esc_read_bec_voltage(uint16_t raw_adc);

/**
 * @brief Оновлення стану лінії BEC за виміряним значенням АЦП.
 * @param driver Вказівник на структуру драйвера ESC.
 * @param raw_adc Сире значення АЦП.
 * @return bec_status_t Поточний статус живлення BEC.
 */
bec_status_t esc_update_bec_status(esc_driver_t *driver, uint16_t raw_adc);

/**
 * @brief Головна функція періодичної обробки стану ESC та BEC.
 * @param driver Вказівник на структуру драйвера ESC.
 * @param raw_adc Сире значення АЦП з каналу моніторингу BEC.
 * @param requested_throttle_us Бажаний імпульс дроселювання від польотного контролера.
 */
void esc_process(esc_driver_t *driver, uint16_t raw_adc, uint16_t requested_throttle_us);

#endif /* ESC_CONTROL_H */
