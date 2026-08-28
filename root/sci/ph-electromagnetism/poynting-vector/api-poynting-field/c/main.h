#ifndef POYNTING_SOLVER_H
#define POYNTING_SOLVER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    double x;
    double y;
    double z;
} poynting_vec3_t;

typedef struct {
    double re;
    double im;
} poynting_complex_t;

typedef struct {
    poynting_complex_t x;
    poynting_complex_t y;
    poynting_complex_t z;
} poynting_cvec3_t;

typedef struct {
    poynting_vec3_t center;
    poynting_vec3_t normal;
    double area;
} poynting_surface_element_t;

typedef struct {
    double active_power_watts;     /* Середня активна потужність Re(S_c) · n */
    double reactive_power_vars;    /* Реактивна потужність Im(S_c) · n */
    double max_flux_density_w_m2;  /* Максимальний модуль вектора Пойнтінга */
    bool status_ok;
} poynting_summary_t;

/* Функция обчислення миттєвого вектора Пойнтінга S = E x H */
poynting_vec3_t poynting_calc_instantaneous(poynting_vec3_t e_field, poynting_vec3_t h_field);

/* Функция обчислення комплексного вектора Пойнтінга S_c = 0.5 * (E_c x H_c*) */
poynting_cvec3_t poynting_calc_complex(poynting_cvec3_t e_comp, poynting_cvec3_t h_comp);

/* Числове інтегрування потоку по масиву елементів поверхні */
poynting_summary_t poynting_integrate_surface(
    const poynting_cvec3_t *e_fields,
    const poynting_cvec3_t *h_fields,
    const poynting_surface_element_t *elements,
    size_t element_count
);

#ifdef __cplusplus
}
#endif

#endif /* POYNTING_SOLVER_H */
