#ifndef COMPENSATION_TABLE_H
#define COMPENSATION_TABLE_H

#include <stdio.h>
#include <stdbool.h>
#include <stddef.h>
#include "abbe_error.h"

/**
 * @file compensation_table.h
 * @brief Оголошення інтерфейсу обробки метрологічних даних та таблиць калібрування.
 *
 * Забезпечує імпорт кутових вимірів лазерного інтерферометра, валідацію дискретної
 * сітки позиціонування вздовж робочого ходу осі, математичний розрахунок поправок
 * та експорт структурованих таблиць для систем ЧПУ й аналітичних звітів у CSV.
 */

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Динамічна структура метрологічної таблиці калібрування.
 */
typedef struct {
    angle_sample_t       *samples;       /* Динамічний масив вихідних кутових вимірів */
    compensation_entry_t *entries;       /* Динамічний масив розрахованих поправок */
    size_t                count;         /* Кількість точок вимірювання */
    size_t                capacity;      /* Виділена місткість буферів пам'яті */
    abbe_arm_t            arm;           /* Задане просторове плече Аббе (dy, dz) */
    angle_unit_t          unit;          /* Одиниці кутових вимірювань */
    double                step_mm;       /* Визначений крок між сусідніми точками */
    bool                  is_calculated; /* Прапорець завершення обчислення поправок */
} compensation_table_t;

/**
 * @brief Метрологічні статистичні показники похибок уздовж осі.
 */
typedef struct {
    size_t count;             /* Кількість точок калібрування */
    double start_pos_mm;      /* Початкова координата осі, мм */
    double end_pos_mm;        /* Кінцева координата осі, мм */
    double step_mm;           /* Номінальний крок переміщення, мм */
    double min_error_um;      /* Найменша (найбільш від'ємна) похибка, мкм */
    double max_error_um;      /* Найбільша (найбільш додатна) похибка, мкм */
    double peak_to_peak_um;   /* Розмах похибки (Peak-to-Peak), мкм */
    double max_correction_um; /* Максимальна за абсолютною величиною поправка, мкм */
} compensation_stats_t;

/**
 * @brief Ініціалізація структури таблиці компенсації.
 *
 * @param table Вказівник на таблицю.
 * @param arm Вказівник на плече Аббе.
 * @param unit Одиниця вимірювання кутів.
 * @return true у разі успішної ініціалізації.
 */
bool comp_table_init(compensation_table_t *table, const abbe_arm_t *arm, angle_unit_t unit);

/**
 * @brief Звільнення виділеної динамічної пам'яті таблиці.
 *
 * @param table Вказівник на таблицю.
 */
void comp_table_free(compensation_table_t *table);

/**
 * @brief Завантаження масиву кутових вимірів із текстового файлу.
 *
 * Рядки мають містити три значення: <Позиція_X_мм> <Pitch> <Yaw>,
 * розділені пробілами, табуляцією або комою. Коментарі (#, ;, //) ігноруються.
 *
 * @param table Вказівник на таблицю.
 * @param filepath Шлях до вхідного файлу вимірів.
 * @return true якщо успішно зчитано принаймні 2 точки.
 */
bool comp_table_load_file(compensation_table_t *table, const char *filepath);

/**
 * @brief Порядковий розбір кутових вимірів із відкритого потоку введення.
 *
 * @param table Вказівник на таблицю.
 * @param stream Вхідний файловий потік (наприклад, файл або stdin).
 * @return true у разі успішного зчитування.
 */
bool comp_table_load_stream(compensation_table_t *table, FILE *stream);

/**
 * @brief Валідація геометрії ходу (монотонне зростання, рівномірність кроку).
 *
 * @param table Вказівник на таблицю.
 * @return true якщо профіль позиціонування коректний для систем ЧПУ.
 */
bool comp_table_validate(compensation_table_t *table);

/**
 * @brief Запуск математичного розрахунку похибок та поправок Аббе для всіх точок.
 *
 * @param table Вказівник на таблицю.
 * @return true у разі успіху.
 */
bool comp_table_compute(compensation_table_t *table);

/**
 * @brief Експорт таблиці лінійних корекцій у форматі CSV.
 *
 * @param table Вказівник на таблицю.
 * @param filepath Шлях до вихідного CSV-файлу.
 * @return true у разі успішного запису.
 */
bool comp_table_export_csv(const compensation_table_t *table, const char *filepath);

/**
 * @brief Експорт таблиці компенсації кроку (Pitch Error Compensation) для систем ЧПУ.
 *
 * Створює структурований текстовий файл поправок, сумісний з промисловими ЧПУ
 * (Fanuc, LinuxCNC, Siemens Sinumerik).
 *
 * @param table Вказівник на таблицю.
 * @param filepath Шлях до вихідного файлу ЧПУ.
 * @param axis_name Назва осі позиціонування (наприклад, "X").
 * @return true у разі успішного запису.
 */
bool comp_table_export_cnc(const compensation_table_t *table, const char *filepath, const char *axis_name);

/**
 * @brief Обчислення метрологічної статистики за розрахованими даними.
 *
 * @param table Вказівник на таблицю.
 * @param stats Вказівник на структуру результатів статистики.
 * @return true якщо статистику успішно обчислено.
 */
bool comp_table_get_stats(const compensation_table_t *table, compensation_stats_t *stats);

#ifdef __cplusplus
}
#endif

#endif /* COMPENSATION_TABLE_H */
