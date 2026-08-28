#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define MAX_LINKS 8
#define MAX_VERTICES 8
#define GRAVITY 9.80665f

/* Параметри однієї ланки робота */
typedef struct {
    float mass;              /* Маса ланки, кг */
    float r[3];              /* Положення центру мас [x, y, z], м */
    float r_ddot[3];         /* Лінійне прискорення [x_ddot, y_ddot, z_ddot], м/с^2 */
    float H_dot[3];          /* Швидкість зміни кутового моменту [Hx_dot, Hy_dot, Hz_dot], Н·м */
} LinkState;

/* 2D вершина опорного багатокутника на поверхні ґрунту (z = 0) */
typedef struct {
    float x;
    float y;
} Point2D;

/* Конфігурація шасі та опорного контуру */
typedef struct {
    Point2D vertices[MAX_VERTICES];
    int num_vertices;
    float dsm_safe_threshold; /* Безпечна дистанція до краю, м (наприклад 0.05 м) */
    float dsm_critical_limit;  /* Критична межа, м (наприклад 0.01 м) */
    float wheel_radius;       /* Радіус тягового колеса, м */
} ChassisConfig;

/* Результат розрахунку стійкості */
typedef struct {
    Point2D zmp;
    float dsm;               /* Dynamic Stability Margin, м */
    float scale_factor;      /* Коефіцієнт масштабування прискорень [0.0 ... 1.0] */
    float feedforward_torque_pitch; /* Випереджальний момент компенсації тангажу, Н·м */
    bool is_stable;
} StabilityOutput;

/* Обчислення координат точки нульового моменту (ZMP) */
Point2D compute_zmp(const LinkState* links, int num_links) {
    float sum_denom = 0.0f;
    float sum_num_x = 0.0f;
    float sum_num_y = 0.0f;

    for (int i = 0; i < num_links; ++i) {
        float effective_gz = GRAVITY + links[i].r_ddot[2];
        float m = links[i].mass;

        sum_denom += m * effective_gz;
        sum_num_x += m * links[i].r[0] * effective_gz - m * links[i].r[2] * links[i].r_ddot[0] - links[i].H_dot[1];
        sum_num_y += m * links[i].r[1] * effective_gz - m * links[i].r[2] * links[i].r_ddot[1] + links[i].H_dot[0];
    }

    Point2D zmp = {0.0f, 0.0f};
    if (fabsf(sum_denom) > 1e-4f) {
        zmp.x = sum_num_x / sum_denom;
        zmp.y = sum_num_y / sum_denom;
    }
    return zmp;
}

/* Обчислення знакової відстані DSM від точки до опуклого багатокутника (вершини проти годинникової стрілки) */
float compute_dsm(Point2D pt, const Point2D* vertices, int num_vertices) {
    float min_dist = 1e6f;

    for (int i = 0; i < num_vertices; ++i) {
        int next = (i + 1) % num_vertices;
        float dx = vertices[next].x - vertices[i].x;
        float dy = vertices[next].y - vertices[i].y;
        float len = sqrtf(dx * dx + dy * dy);

        if (len < 1e-5f) continue;

        /* Внутрішня нормаль: [-dy/len, dx/len] */
        float nx = -dy / len;
        float ny = dx / len;

        /* Знакова відстань до прямої ребра */
        float dist = (pt.x - vertices[i].x) * nx + (pt.y - vertices[i].y) * ny;
        if (dist < min_dist) {
            min_dist = dist;
        }
    }
    return min_dist;
}

/* Головний крок захисту в циклі реального часу */
StabilityOutput evaluate_stability_guard(
    const LinkState* links, int num_links,
    const ChassisConfig* cfg) 
{
    StabilityOutput out;
    out.zmp = compute_zmp(links, num_links);
    out.dsm = compute_dsm(out.zmp, cfg->vertices, cfg->num_vertices);

    /* Оцінка коефіцієнта безпеки */
    if (out.dsm >= cfg->dsm_safe_threshold) {
        out.scale_factor = 1.0f;
        out.is_stable = true;
    } else if (out.dsm <= cfg->dsm_critical_limit) {
        out.scale_factor = 0.0f; /* Повне блокування подальшого розгону */
        out.is_stable = false;
    } else {
        /* Лінійна інтерполяція гальмування при наближенні до межі */
        out.scale_factor = (out.dsm - cfg->dsm_critical_limit) / 
                           (cfg->dsm_safe_threshold - cfg->dsm_critical_limit);
        out.is_stable = true;
    }

    /* Розрахунок реактивного моменту для випереджальної компенсації на мотори шасі */
    float net_reaction_moment_y = 0.0f;
    for (int i = 0; i < num_links; ++i) {
        net_reaction_moment_y += links[i].mass * links[i].r[2] * links[i].r_ddot[0] + links[i].H_dot[1];
    }
    /* Випереджальний момент на колеса спрямований назустріч реактивному моменту */
    out.feedforward_torque_pitch = -net_reaction_moment_y;

    return out;
}
