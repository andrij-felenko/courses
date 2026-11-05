#ifndef ABBE_ERROR_H
#define ABBE_ERROR_H

#include <stddef.h>
#include <stdbool.h>

/**
 * @file abbe_error.h
 * @brief Оголошення C-інтерфейсу обчислення похибки Аббе першого порядку.
 *
 * Модуль реалізує фізичну та геометричну модель виникнення похибки Аббе
 * під час лінійного позиціонування вузлів (кареток верстатів, вимірювальних столів).
 * Кутові перекоси каретки навколо осей Y (pitch, тангаж) та Z (yaw, рискання)
 * у поєднанні з просторовим плечем зміщення вимірювальної осі (dy, dz)
 * спричиняють паразитне лінійне зміщення вздовж лінії переміщення X.
 */

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Одиниці вимірювання кутових величин.
 */
typedef enum {
    ANGLE_UNIT_ARCSEC = 0, /* Кутові секунди (arcsec, ") */
    ANGLE_UNIT_URAD   = 1, /* Мікрорадіани (urad, мкрад) */
    ANGLE_UNIT_MRAD   = 2, /* Мілірадіани (mrad, мрад) */
    ANGLE_UNIT_RAD    = 3  /* Радіани (rad) */
} angle_unit_t;

/**
 * @brief Коефіцієнти точного переведення кутових одиниць у радіани.
 * 1 кутова секунда = pi / (180 * 3600) rad ≈ 4.84813681109536e-6 rad.
 */
#define ABBE_ARCSEC_TO_RAD (4.8481368110953599359e-6)
#define ABBE_URAD_TO_RAD   (1.0e-6)
#define ABBE_MRAD_TO_RAD   (1.0e-3)

/**
 * @brief Просторове плече Аббе (Abbe offset vector).
 *
 * Визначає відстань між номінальною лінією переміщення/вимірювання напрямної
 * та реальною функціональною точкою (кінцем щупа, центром фрези тощо).
 */
typedef struct {
    double dy; /* Зміщення вимірювальної осі вздовж осі Y (горизонтальне плече), мм */
    double dz; /* Зміщення вимірювальної осі вздовж осі Z (вертикальне плече), мм */
} abbe_arm_t;

/**
 * @brief Дискретна вибірка кутових відхилень інтерферометра або автоколіматора.
 */
typedef struct {
    double position_x; /* Позиція каретки вздовж осі переміщення X, мм */
    double pitch;      /* Кутове відхилення тангажу (навколо осі Y) у вхідних одиницях */
    double yaw;        /* Кутове відхилення рискання (навколо осі Z) у вхідних одиницях */
} angle_sample_t;

/**
 * @brief Результат розрахунку лінійної компенсації для однієї точки осі.
 */
typedef struct {
    double position_x;      /* Номінальна координата X, мм */
    double pitch_rad;       /* Тангаж, переведений у радіани */
    double yaw_rad;         /* Рискання, переведене у радіани */
    double error_pitch_mm;  /* Лінійна похибка від тангажу (dz * pitch), мм */
    double error_yaw_mm;    /* Лінійна похибка від рискання (dy * yaw), мм */
    double total_error_mm;  /* Сумарна поздовжня похибка Аббе першого порядку, мм */
    double correction_mm;   /* Компенсуюча поправка (-total_error_mm), мм */
} compensation_entry_t;

/**
 * @brief Переведення кутової величини з вибраної одиниці в радіани.
 *
 * @param angle Значення кута у вихідних одиницях.
 * @param unit Тип кутової одиниці вимірювання.
 * @return Значення кута в радіанах.
 */
double abbe_angle_to_radians(double angle, angle_unit_t unit);

/**
 * @brief Парсинг рядка з назвою одиниці вимірювання.
 *
 * Підтримує варіанти: "arcsec", "sec", "as", "urad", "mrad", "rad".
 *
 * @param str Рядок із назвою одиниці.
 * @param out_unit Вказівник для збереження результату.
 * @return true у разі успішного розпізнавання, false якщо назва невідома.
 */
bool abbe_parse_unit(const char *str, angle_unit_t *out_unit);

/**
 * @brief Отримання рядкового позначення кутової одиниці вимірювання.
 *
 * @param unit Тип одиниці.
 * @return Статичний рядковий літерал.
 */
const char *abbe_unit_to_string(angle_unit_t unit);

/**
 * @brief Розрахунок лінійної похибки Аббе першого порядку для однієї точки.
 *
 * @param arm Вказівник на компоненти плеча Аббе (dy, dz).
 * @param sample Вказівник на виміряні значення кутів.
 * @param unit Одиниця вимірювання кутів у вибірці.
 * @param out_entry Вказівник на структуру для збереження результату.
 * @return true у разі успішного обчислення, false при помилці аргументів.
 */
bool abbe_calculate_point(const abbe_arm_t *arm,
                          const angle_sample_t *sample,
                          angle_unit_t unit,
                          compensation_entry_t *out_entry);

/**
 * @brief Пакетний розрахунок похибок Аббе для масиву точок робочого ходу.
 *
 * @param arm Вказівник на компоненти плеча Аббе.
 * @param samples Масив дискретних вибірок кутів.
 * @param count Кількість точок у масиві.
 * @param unit Одиниця вимірювання вхідних кутів.
 * @param out_entries Масив для запису розрахованих поправок.
 * @return true у разі успіху, false при некоректних даних.
 */
bool abbe_calculate_batch(const abbe_arm_t *arm,
                          const angle_sample_t *samples,
                          size_t count,
                          angle_unit_t unit,
                          compensation_entry_t *out_entries);

#ifdef __cplusplus
}
#endif

#endif /* ABBE_ERROR_H */
