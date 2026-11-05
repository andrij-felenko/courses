#ifndef ORGANIZER_CALC_H
#define ORGANIZER_CALC_H

#include <stddef.h>
#include <stdbool.h>

#define GRIDFINITY_PITCH_MM 42.0
#define ESD_LIMIT_TIME_SEC 2.0
#define ESD_LIMIT_VOLTAGE_RATIO 0.1

/* Перелік стандартних рядів радіокомпонентів */
typedef enum {
    EROW_E12,
    EROW_E24
} ERowSeries;

/* Геометрія та параметри деталі для пакування */
typedef struct {
    double length_mm;      /* Довжина деталі */
    double width_mm;       /* Ширина деталі */
    double height_mm;      /* Висота деталі */
    size_t count;          /* Кількість деталей у комірці */
} PartSpec;

/* Результати розрахунку комірки */
typedef struct {
    double part_volume_mm3;     /* Об'єм однієї деталі */
    double bulk_volume_mm3;     /* Насипний об'єм деталей */
    double required_volume_mm3; /* Необхідний об'єм комірки з урахуванням кліренсу */
    double inner_width_mm;      /* Рекомендована внутрішня ширина комірки */
    double inner_length_mm;     /* Рекомендована внутрішня довжина комірки */
    double inner_height_mm;     /* Рекомендована внутрішня глибина комірки */
    size_t grid_units_x;        /* Розмір у кроках Gridfinity (по 42 мм) за X */
    size_t grid_units_y;        /* Розмір у кроках Gridfinity за Y */
} CellCalculation;

/* Параметри матеріалу та розрахунок ESD-безпеки за IEC 61340-5-1 */
typedef struct {
    double surface_resistivity_ohm_sq; /* Поверхневий опір, Ом/квадрат */
    double capacitance_pf;             /* Еквівалентна ємність зразка, пФ */
    double initial_voltage_v;          /* Початковий трибоелектричний потенціал, В */
    double target_voltage_v;           /* Цільовий безпечний потенціал, В */
    double decay_time_sec;             /* Розрахований час стікання заряду, с */
    bool is_esd_safe;                  /* Чи вкладається час розпаду у вимогу <= 2.0 с */
} EsdCalculation;

/* Конфігурація матриці касетного блоку */
typedef struct {
    ERowSeries series;         /* Серія E12 або E24 */
    size_t total_compartments; /* Кількість комірок під номінали */
    size_t columns;            /* Оптимальна кількість колонок */
    size_t rows;               /* Оптимальна кількість рядків */
    double wall_thickness_mm;  /* Товщина міжкоміркових перегородок, мм */
    double total_width_mm;     /* Загальна габаритна ширина матриці, мм */
    double total_length_mm;    /* Загальна габаритна довжина матриці, мм */
} MatrixLayout;

/* Функції розрахунку */
CellCalculation calc_cell_dimensions(const PartSpec *part, double packing_density, double safety_margin);
EsdCalculation calc_esd_decay(double surface_resistivity, double capacitance_pf, double v_init, double v_target);
MatrixLayout calc_optimal_matrix(ERowSeries series, double cell_w, double cell_l, double wall_th);

#endif /* ORGANIZER_CALC_H */
