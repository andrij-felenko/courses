#ifndef MAGNET_CALC_H
#define MAGNET_CALC_H

#include <stdbool.h>

/**
 * @brief Параметри циліндричного аксіально намагніченого неодимового магніту
 */
typedef struct {
    const char *grade;         /* Марка сплаву, наприклад "N35" або "N52" */
    double diameter_mm;        /* Зовнішній діаметр магніту D, мм */
    double thickness_mm;       /* Товщина/висота магніту h, мм */
    double br_tesla;           /* Залишкова магнітна індукція Br, Тл */
} DiscMagnet;

/**
 * @brief Геометричні параметри посадкового гнізда та клейового зазору
 */
typedef struct {
    double pocket_dia_mm;             /* Діаметр гнізда в корпусі, мм */
    double pocket_depth_mm;           /* Глибина гнізда, мм */
    double glue_gap_mm;               /* Товщина клейового шва, мм */
    double glue_shear_strength_mpa;   /* Допустиме напруження зсуву клею, МПа */
} PocketFit;

/**
 * @brief Конфігурація важеля магнітної кришки
 */
typedef struct {
    double magnet_arm_mm;      /* Відстань від петлі до центру магніту, мм */
    double handle_arm_mm;      /* Відстань від петлі до ручки відкривання, мм */
    double friction_coeff;     /* Коефіцієнт тертя при зсуві (сталь по Ni) */
} CoverLatchConfig;

/**
 * @brief Зведений звіт розрахунку магнітного вузла
 */
typedef struct {
    double pole_area_mm2;             /* Площа робочого полюса, мм² */
    double b_surface_tesla;           /* Індукція на поверхні зазору, Тл */
    double pull_force_n;              /* Сила відриву по нормалі, Н */
    double shear_force_n;             /* Сила зсуву, Н */
    double glue_area_mm2;             /* Ефективна площа контакту з клеєм, мм² */
    double glue_shear_stress_mpa;     /* Розрахункове напруження зсуву клею, МПа */
    double safety_factor;             /* Коефіцієнт запасу міцності клейового шва */
    double opening_force_n;           /* Зусилля відкривання на ручці кришки, Н */
    bool is_glue_safe;                /* Чи витримує клей зусилля відриву */
} LatchReport;

/**
 * @brief Обчислення площі круглого полюса магніту
 */
double calc_pole_area_mm2(double diameter_mm);

/**
 * @brief Обчислення індукції B(z) на осі циліндричного магніту на відстані z
 */
double calc_axial_flux_density(const DiscMagnet *magnet, double air_gap_mm);

/**
 * @brief Обчислення сили притягання до масивної сталевої плити (за формулою Максвелла)
 */
double calc_maxwell_pull_force_n(double b_tesla, double pole_area_mm2);

/**
 * @brief Повний розрахунок посадки магніту, клейового шва та механізму кришки
 */
bool evaluate_magnet_latch(const DiscMagnet *magnet,
                          const PocketFit *fit,
                          const CoverLatchConfig *latch,
                          double air_gap_mm,
                          LatchReport *out_report);

#endif /* MAGNET_CALC_H */
