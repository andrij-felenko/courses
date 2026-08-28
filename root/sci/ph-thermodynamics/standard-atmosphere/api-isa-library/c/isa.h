/*
 * isa.h — C API для роботи з Міжнародною стандартною атмосферою (ISA ISO 2533)
 */
#ifndef ISA_LIBRARY_H
#define ISA_LIBRARY_H

#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ── Константи ISA ISO 2533:1975 ────────────────────────────────────────── */
#define ISA_G0            9.80665      /* Стандартне прискорення вільного падіння, м/с² */
#define ISA_R_SPEC        287.05287    /* Питома газова стала сухого повітря, Дж/(кг·К) */
#define ISA_EARTH_RADIUS  6356766.0    /* Ефективний геопотенціальний радіус Землі, м */
#define ISA_GAMMA_AIR     1.40         /* Показник адіабати сухого повітря */
#define ISA_SUTHERLAND_S  110.4        /* Константа Сазерленда, K */
#define ISA_SUTHERLAND_B  1.458e-6     /* Коефіцієнт в'язкості Сазерленда, кг/(м·с·K¹/²) */

#define ISA_P0            101325.0     /* Тиск на рівні моря, Па */
#define ISA_T0            288.15       /* Температура на рівні моря, K */
#define ISA_RHO0          1.2250       /* Густина на рівні моря, кг/м³ */
#define ISA_MAX_H_METERS  84852.0      /* Максимальна геопотенціальна висота, м */

/* ── Перелік кодових статусах помилок ────────────────────────────────────── */
typedef enum {
    ISA_SUCCESS = 0,               /* Успішне виконання */
    ISA_ERROR_NULL_POINTER = -1,   /* Передано нульовий вказівник */
    ISA_ERROR_OUT_OF_BOUNDS = -2,  /* Висота поза допустимим діапазоном 0..84852 м */
    ISA_ERROR_INVALID_PARAM = -3   /* Невалідний фізичний параметр */
} isa_error_t;

/* ── Повний термодинамічний стан атмосфери ──────────────────────────────── */
typedef struct {
    double h_geopotential; /* Геопотенціальна висота h, м */
    double z_geometric;    /* Реальна геометрична висота Z, м */
    double temperature;    /* Абсолютна температура T, K */
    double temp_celsius;   /* Температура, °C */
    double pressure;       /* Статичний тиск P, Па */
    double density;        /* Густина повітря ρ, кг/м³ */
    double sound_speed;    /* Місцева швидкість звуку a, м/с */
    double dynamic_visc;   /* Динамічна в'язкість μ, кг/(м·с) */
    double kinematic_visc; /* Кінематична в'язкість ν, м²/с */
} isa_state_t;

/* ── Публічна поверхня C API ────────────────────────────────────────────── */

/* Перетворення геометричної висоти Z у геопотенціальну h */
double isa_z_to_h(double z_geometric_m);

/* Перетворення геопотенціальної висоти h у геометричну Z */
double isa_h_to_z(double h_geopotential_m);

/* Основний розрахунок стану атмосфери за геопотенціальною висотою h */
isa_error_t isa_evaluate(double h_geopotential_m, isa_state_t *result);

/* Обчислення барометричної висоти h_p у тропосфері за тиском P */
isa_error_t isa_get_pressure_altitude(double pressure_pa, double *h_p_m);

/* Обчислення висоти за густиною h_d за фактичним тиском та температурою */
isa_error_t isa_get_density_altitude(double pressure_pa, double temp_k, double *h_d_m);

/* Перерахунок індикаторної швидкості CAS у істинну TAS */
double isa_cas_to_tas(double cas_ms, double density_kg_m3);

/* Перерахунок істинної швидкості TAS у число Маха */
double isa_tas_to_mach(double tas_ms, double sound_speed_ms);

#ifdef __cplusplus
}
#endif

#endif /* ISA_LIBRARY_H */
