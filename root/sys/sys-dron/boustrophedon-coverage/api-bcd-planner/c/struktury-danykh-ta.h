#ifndef BCD_PLANNER_H
#define BCD_PLANNER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди повернення та помилок планувальника */
typedef enum {
    BCD_STATUS_OK = 0,
    BCD_STATUS_INVALID_ARGUMENT = -1,
    BCD_STATUS_NON_CONVEX_HOLE = -2,
    BCD_STATUS_SELF_INTERSECTING = -3,
    BCD_STATUS_OUT_OF_MEMORY = -4,
    BCD_STATUS_DECOMPOSITION_FAILED = -5,
    BCD_STATUS_NO_VALID_PATH = -6
} bcd_status_t;

/* Стратегія вибору кута замітання */
typedef enum {
    BCD_ANGLE_FIXED = 0,             /* Заданий користувачем фіксований кут */
    BCD_ANGLE_AUTO_LONGEST_EDGE = 1,  /* Автоматичний вибір вздовж найдовшого ребра */
    BCD_ANGLE_AUTO_MIN_TURNS = 2     /* Повний перебір для мінімізації поворотів */
} bcd_angle_mode_t;

/* Точка у 2D декартовій системі координат (метри) */
typedef struct {
    double x;
    double y;
} bcd_point_t;

/* Конфігураційні параметри планувальника покриття */
typedef struct {
    double swath_width;              /* Фізична ширина захвату сенсора/інструмента (м) */
    double lateral_overlap;          /* Коефіцієнт перекриття [0.0 .. 0.9] */
    double safety_margin;            /* Захисний відступ від меж та перешкод (м) */
    double min_turn_radius;          /* Мінімальний радіус розвороту апарата (м) */
    bcd_angle_mode_t angle_mode;     /* Режим визначення кута замітання */
    double custom_sweep_angle_rad;   /* Кут замітання при режимі BCD_ANGLE_FIXED */
} bcd_config_t;

/* Статистика та метрики сформованого плану */
typedef struct {
    size_t cell_count;               /* Кількість отриманих монотонних комірок */
    size_t stripe_count;             /* Загальна кількість робочих галсів */
    size_t turn_count;               /* Загальна кількість розворотів */
    double total_work_distance_m;    /* Довжина корисних робочих проходів (м) */
    double total_transit_distance_m; /* Довжина міжкоміркових перельотів/переїздів (м) */
    double estimated_area_m2;        /* Покрита корисна площа (м²) */
} bcd_metrics_t;

/* Непрозорий дескриптор об'єкта планувальника */
typedef struct bcd_context bcd_context_t;

/* Створення та знищення контексту планувальника */
bcd_context_t* bcd_create(const bcd_config_t *config);
void bcd_destroy(bcd_context_t *ctx);

/* Задання геометрії середовища */
bcd_status_t bcd_set_boundary(bcd_context_t *ctx, const bcd_point_t *vertices, size_t count);
bcd_status_t bcd_add_obstacle(bcd_context_t *ctx, const bcd_point_t *vertices, size_t count);
void bcd_clear_obstacles(bcd_context_t *ctx);

/* Виконання розкладу та планування місії */
bcd_status_t bcd_compute(bcd_context_t *ctx);

/* Отримання результатів планування */
bcd_status_t bcd_get_waypoint_count(const bcd_context_t *ctx, size_t *out_count);
bcd_status_t bcd_get_waypoints(const bcd_context_t *ctx, bcd_point_t *out_buffer, size_t buffer_size);
bcd_status_t bcd_get_metrics(const bcd_context_t *ctx, bcd_metrics_t *out_metrics);

#ifdef __cplusplus
}
#endif

#endif /* BCD_PLANNER_H */
