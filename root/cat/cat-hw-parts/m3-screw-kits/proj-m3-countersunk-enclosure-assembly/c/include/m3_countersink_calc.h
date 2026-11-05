#ifndef M3_COUNTERSINK_CALC_H
#define M3_COUNTERSINK_CALC_H

#include <stdbool.h>

/* Стандартні розміри для гвинта з потайною голівкою М3 (DIN 7991 / ISO 10642) */
#define M3_DIAMETER_NOMINAL     3.0f   /* Номінальний діаметр різьби, мм */
#define M3_HEAD_DIAMETER        6.0f   /* Зовнішній діаметр потайної голівки d_k, мм */
#define M3_HOLE_DIAMETER        3.4f   /* Діаметр отвору під з'єднання d_h, мм */
#define M3_COUNTERSINK_ANGLE    90.0f  /* Кут зенкування, град */

/* Класи міцності гвинтів */
typedef enum {
    SCREW_CLASS_8_8,
    SCREW_CLASS_10_9,
    SCREW_CLASS_12_9,
    SCREW_CLASS_A2_70
} ScrewClass;

/* Матеріали корпусу / панелі */
typedef enum {
    MATERIAL_ALUMINUM_6061_T6, /* Алюмінієвий сплав */
    MATERIAL_STEEL_Q235,       /* Конструкційна сталь */
    MATERIAL_BRASS_C36000,     /* Латунь */
    MATERIAL_PLASTIC_ABS       /* Термопластик ABS */
} HousingMaterial;

/* Структура геометричних та міцнісних параметрів з'єднання */
typedef struct {
    float plate_thickness;     /* Товщина листа/панелі t_plate, мм */
    float countersink_depth;   /* Глибина конуса h_k, мм */
    float residual_thickness;  /* Залишкова товщина стінки (поясок) t_rem, мм */
    bool knife_edge_risk;      /* Прапорець ризику виникнення ножового краю */
} GeometryResult;

/* Структура результатів силового розрахунку */
typedef struct {
    float preload_force_n;     /* Попереднє зусилля затягування F_p, Н */
    float tightening_torque_nm;/* Граничний момент затягування M_tight, Н*м */
    float contact_pressure_mpa;/* Контактний тиск під голівкою p_contact, МПа */
    float allowable_pressure_mpa;/* Допустимий тиск для матеріалу, МПа */
    bool pressure_exceeded;    /* Прапорець перевищення допустимого тиску */
} StrengthResult;

/**
 * @brief Розраховує геометричні параметри зенкування та перевіряє наявність ножового краю.
 * 
 * @param plate_thickness Товщина листа в міліметрах.
 * @param out_geom Покажчик на структуру для збереження результатів геометрії.
 * @return true якщо параметри в нормі, false у разі критичних помилок вхідних даних.
 */
bool calc_geometry(float plate_thickness, GeometryResult *out_geom);

/**
 * @brief Обчислює допустиме попереднє зусилля та момент затягування гвинта М3.
 * 
 * @param screw_cls Клас міцності гвинта.
 * @param friction_coeff Коефіцієнт тертя у різьбі та під голівкою.
 * @return Попереднє зусилля F_p у ньютонах.
 */
float calc_screw_preload(ScrewClass screw_cls, float friction_coeff);

/**
 * @brief Розраховує момент затягування за зусиллям натягу та номінальним діаметром.
 * 
 * @param preload_n Попереднє зусилля, Н.
 * @param nominal_d Номінальний діаметр, мм.
 * @param friction_coeff Коефіцієнт тертя.
 * @return Момент затягування, Н*м.
 */
float calc_tightening_torque(float preload_n, float nominal_d, float friction_coeff);

/**
 * @brief Виконує повний перевірочний розрахунок з'єднання (геометрія + міцність + контактний тиск).
 * 
 * @param plate_thickness Товщина листа, мм.
 * @param material Матеріал корпусу.
 * @param screw_cls Клас міцності гвинта.
 * @param friction_coeff Коефіцієнт тертя.
 * @param out_geom Результати геометрії.
 * @param out_strength Результати міцнісного аналізу.
 * @return true якщо з'єднання надійне, false якщо є ризики руйнування чи ножового краю.
 */
bool verify_m3_countersink_joint(float plate_thickness,
                                 HousingMaterial material,
                                 ScrewClass screw_cls,
                                 float friction_coeff,
                                 GeometryResult *out_geom,
                                 StrengthResult *out_strength);

#endif /* M3_COUNTERSINK_CALC_H */
