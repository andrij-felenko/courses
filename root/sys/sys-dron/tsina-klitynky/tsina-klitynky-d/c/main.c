#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define COST_FREE_SPACE          0
#define COST_INSCRIBED_OBSTACLE  253
#define COST_LETHAL_OBSTACLE     254
#define COST_NO_INFORMATION      255

typedef struct {
    float resolution;           /* Розмір клітинки в метрах */
    float inscribed_radius;     /* Вписаний радіус дрона (м) */
    float inflation_radius;     /* Зовнішній радіус інфляції (м) */
    float cost_scaling_factor;  /* Коефіцієнт альфа експоненційного спаду */
    float cost_weight;          /* Вага штрафу вартості (k_cost) */
    float turn_penalty_weight;  /* Вага штрафу за поворот (k_turn) */
} CostmapConfig;

/* Розрахунок інфляційної вартості за відстанню до найближчої перешкоди */
uint8_t compute_inflation_cost(float dist_to_obstacle, const CostmapConfig* cfg) {
    if (dist_to_obstacle <= cfg->inscribed_radius) {
        return COST_INSCRIBED_OBSTACLE;
    }
    if (dist_to_obstacle >= cfg->inflation_radius) {
        return COST_FREE_SPACE;
    }
    
    float delta_d = dist_to_obstacle - cfg->inscribed_radius;
    float factor = expf(-cfg->cost_scaling_factor * delta_d);
    float cost = factor * (float)(COST_INSCRIBED_OBSTACLE - 1);
    
    if (cost < 1.0f) {
        return COST_FREE_SPACE;
    }
    return (uint8_t)cost;
}

/* Обчислення повної вартості переходу між двома вузлами сітки */
float compute_step_cost(int from_x, int from_y,
                          int to_x, int to_y,
                          int prev_x, int prev_y,
                          uint8_t cell_cost,
                          const CostmapConfig* cfg) {
    if (cell_cost >= COST_INSCRIBED_OBSTACLE) {
        return INFINITY; /* Непрохідна зона */
    }

    int dx = to_x - from_x;
    int dy = to_y - from_y;
    
    /* Геометрична евклідова відстань кроку */
    float step_dist = (dx != 0 && dy != 0) ? (1.41421356f * cfg->resolution) 
                                           : (1.0f * cfg->resolution);

    /* Штраф за вартість клітинки (інфляція + динамічні шари) */
    float cost_factor = 1.0f + cfg->cost_weight * ((float)cell_cost / 254.0f);
    float traversal_cost = step_dist * cost_factor;

    /* Кінематичний штраф за зміну напрямку руху */
    float turn_penalty = 0.0f;
    if (prev_x != from_x || prev_y != from_y) {
        int dir1_x = from_x - prev_x;
        int dir1_y = from_y - prev_y;
        int dir2_x = dx;
        int dir2_y = dy;

        float dot = (float)(dir1_x * dir2_x + dir1_y * dir2_y);
        float len1 = sqrtf((float)(dir1_x * dir1_x + dir1_y * dir1_y));
        float len2 = sqrtf((float)(dir2_x * dir2_x + dir2_y * dir2_y));

        if (len1 > 0.0f && len2 > 0.0f) {
            float cos_theta = dot / (len1 * len2);
            if (cos_theta > 1.0f) cos_theta = 1.0f;
            if (cos_theta < -1.0f) cos_theta = -1.0f;
            turn_penalty = cfg->turn_penalty_weight * (1.0f - cos_theta);
        }
    }

    return traversal_cost + turn_penalty;
}
