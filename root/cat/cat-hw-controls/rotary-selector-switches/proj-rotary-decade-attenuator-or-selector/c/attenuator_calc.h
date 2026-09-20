#ifndef ATTENUATOR_CALC_H
#define ATTENUATOR_CALC_H

#include <stddef.h>
#include <stdbool.h>

#define ATTENUATOR_MAX_STEPS 32

// Перелік характеристик згасання атенюатора
typedef enum {
    ATTENUATION_LOGARITHMIC = 0, // Логарифмічна крива (рівномірний крок згасання у децибелах)
    ATTENUATION_LINEAR,          // Лінійна крива (рівномірний крок відношення напруги)
    ATTENUATION_ANTILOGARITHMIC  // Антилогарифмічна крива
} attenuator_taper_t;

// Перелік стандартних рядів E-серій резисторів для апроксимації
typedef enum {
    ESERIES_NONE = 0, // Без апроксимації (використання ідеальних розрахованих опорів)
    ESERIES_E24,      // Стандартний ряд E24 (допуск 5%)
    ESERIES_E96       // Прецизійний ряд E96 (допуск 1%)
} eseries_type_t;

// Структура збереження розрахованих параметрів одного кроку перемикача
typedef struct {
    size_t step_index;             // Номер позиції галетного перемикача (0 .. num_steps - 1)
    double ideal_attenuation_db;   // Цільове згасання на даному кроці у дБ
    double ideal_resistor_ohm;     // Теоретичний розрахований опір резистивної секції, Ом
    double actual_resistor_ohm;    // Апроксимований номінал резистора із ряду E24/E96, Ом
    double actual_attenuation_db;  // Фактичне розраховане згасання у дБ з урахуванням номіналів та імпедансу
    double error_db;               // Абсолютна похибка згасання (actual_db - ideal_db), дБ
    double error_percent;          // Відносна похибка згасання у відсотках
} attenuator_step_t;

// Структура конфігурації розрахунку резистивного атенюатора
typedef struct {
    double total_resistance_ohm;   // Номінальний загальний опір дільника (наприклад, 10000.0 Ом)
    double source_impedance_ohm;   // Вихідний імпеданс джерела сигналу R_s, Ом
    double load_impedance_ohm;     // Вхідний імпеданс навантаження R_L, Ом (0.0 — нехтувати)
    double max_attenuation_db;     // Максимальне згасання на нульовій позиції (наприклад, -55.0 дБ)
    size_t num_steps;              // Кількість позицій галетного перемикача
    attenuator_taper_t taper;      // Тип характеристики згасання
    eseries_type_t eseries;        // Стандартний ряд E-серії для квантування номіналів
} attenuator_config_t;

// Знаходження найближчого стандартного номіналу з ряду E24 чи E96
double find_nearest_eseries(double value_ohm, eseries_type_t series);

// Основна функція розрахунку резистивної драбини атенюатора
bool attenuator_calculate(const attenuator_config_t *config,
                         attenuator_step_t *steps_out,
                         size_t max_steps_out,
                         size_t *actual_steps_count);

#endif // ATTENUATOR_CALC_H
