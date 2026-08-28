#ifndef LIBSCHWARZIAN_H
#define LIBSCHWARZIAN_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SCHWARZIAN_OK = 0,
    SCHWARZIAN_ERR_CRITICAL = -1,
    SCHWARZIAN_ERR_ZERO_STEP = -2,
    SCHWARZIAN_ERR_NULL_PTR = -3
} schwarzian_status_t;

typedef double (*schwarzian_map_fn)(double x, const void *user_data);
typedef void (*schwarzian_deriv_fn)(double x, double *df1, double *df2, double *df3, const void *user_data);

typedef struct {
    double x;
    double df1;
    double df2;
    double df3;
    double schwarzian;
} schwarzian_point_t;

typedef struct {
    double h;            /* Крок диференціювання (за замовчуванням 1e-4) */
    double eps_critical; /* Поріг критичної точки (за замовчуванням 1e-9) */
} schwarzian_config_t;

/* Створення конфігурації за замовчуванням */
schwarzian_config_t schwarzian_config_default(void);

/* Прямий обчислювач за значеннями похідних */
schwarzian_status_t schwarzian_eval_exact(double df1, double df2, double df3, 
                                           double eps_critical, double *out_sf);

/* Обчислення похідної Шварца у точці з точними похідними */
schwarzian_status_t schwarzian_eval_point(schwarzian_deriv_fn deriv, double x, 
                                            const void *user_data,
                                            schwarzian_config_t config,
                                            schwarzian_point_t *out_pt);

/* Чисельне оцінювання похідної Шварца через 5-точкову схему */
schwarzian_status_t schwarzian_eval_numeric(schwarzian_map_fn map, double x,
                                              const void *user_data,
                                              schwarzian_config_t config,
                                              schwarzian_point_t *out_pt);

/* Сканування інтервалу на від'ємність Шварціана S(f) < 0 */
schwarzian_status_t schwarzian_check_singer_condition(schwarzian_map_fn map,
                                                       double x_min, double x_max,
                                                       size_t num_samples,
                                                       schwarzian_config_t config,
                                                       int *out_is_negative_everywhere);

#ifdef __cplusplus
}
#endif

#endif /* LIBSCHWARZIAN_H */
