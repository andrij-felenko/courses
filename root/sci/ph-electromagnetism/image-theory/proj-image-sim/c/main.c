#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define K_COULOMB 8.9875517923e9

typedef struct {
    double x;
    double y;
    double z;
} es_vec3_t;

typedef struct {
    es_vec3_t pos;
    double charge;
    bool is_image;
} es_point_charge_t;

typedef enum {
    GEOM_PLANE,
    GEOM_SPHERE,
    GEOM_CORNER_90
} es_geometry_type_t;

typedef struct {
    es_geometry_type_t geom_type;
    es_point_charge_t* real_charges;
    size_t real_count;
    es_point_charge_t* image_charges;
    size_t image_count;

    double plane_z;
    es_vec3_t sphere_center;
    double sphere_radius;
} es_solver_t;

static inline double vec3_length_sq(es_vec3_t v) {
    return v.x * v.x + v.y * v.y + v.z * v.z;
}

static inline double vec3_length(es_vec3_t v) {
    return sqrt(vec3_length_sq(v));
}

static inline es_vec3_t vec3_sub(es_vec3_t a, es_vec3_t b) {
    return (es_vec3_t){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline es_vec3_t vec3_scale(es_vec3_t v, double s) {
    return (es_vec3_t){v.x * s, v.y * s, v.z * s};
}

es_solver_t* es_solver_create(void) {
    es_solver_t* s = (es_solver_t*)calloc(1, sizeof(es_solver_t));
    if (!s) return NULL;
    s->geom_type = GEOM_PLANE;
    s->plane_z = 0.0;
    return s;
}

void es_solver_destroy(es_solver_t* s) {
    if (!s) return;
    free(s->real_charges);
    free(s->image_charges);
    free(s);
}

bool es_solver_add_charge(es_solver_t* s, es_vec3_t pos, double q) {
    es_point_charge_t* new_arr = (es_point_charge_t*)realloc(
        s->real_charges, (s->real_count + 1) * sizeof(es_point_charge_t));
    if (!new_arr) return false;

    s->real_charges = new_arr;
    s->real_charges[s->real_count++] = (es_point_charge_t){pos, q, false};
    return true;
}

void es_solver_rebuild_images(es_solver_t* s) {
    free(s->image_charges);
    s->image_charges = NULL;
    s->image_count = 0;

    if (s->geom_type == GEOM_PLANE) {
        s->image_charges = (es_point_charge_t*)malloc(s->real_count * sizeof(es_point_charge_t));
        s->image_count = s->real_count;
        for (size_t i = 0; i < s->real_count; ++i) {
            es_vec3_t pos = s->real_charges[i].pos;
            pos.z = 2.0 * s->plane_z - pos.z;
            s->image_charges[i] = (es_point_charge_t){pos, -s->real_charges[i].charge, true};
        }
    } else if (s->geom_type == GEOM_SPHERE) {
        s->image_charges = (es_point_charge_t*)malloc(s->real_count * sizeof(es_point_charge_t));
        s->image_count = s->real_count;
        for (size_t i = 0; i < s->real_count; ++i) {
            es_vec3_t rel = vec3_sub(s->real_charges[i].pos, s->sphere_center);
            double d = vec3_length(rel);
            double d_img = (s->sphere_radius * s->sphere_radius) / d;
            es_vec3_t img_pos = {
                s->sphere_center.x + rel.x * (d_img / d),
                s->sphere_center.y + rel.y * (d_img / d),
                s->sphere_center.z + rel.z * (d_img / d)
            };
            double img_q = -s->real_charges[i].charge * (s->sphere_radius / d);
            s->image_charges[i] = (es_point_charge_t){img_pos, img_q, true};
        }
    }
}

double es_solver_eval_potential(const es_solver_t* s, es_vec3_t p) {
    double v_total = 0.0;
    for (size_t i = 0; i < s->real_count; ++i) {
        double dist = vec3_length(vec3_sub(p, s->real_charges[i].pos));
        if (dist > 1e-12) v_total += K_COULOMB * s->real_charges[i].charge / dist;
    }
    for (size_t i = 0; i < s->image_count; ++i) {
        double dist = vec3_length(vec3_sub(p, s->image_charges[i].pos));
        if (dist > 1e-12) v_total += K_COULOMB * s->image_charges[i].charge / dist;
    }
    return v_total;
}

int main(void) {
    printf("=== Моделювання поля методом дзеркальних зображень (C) ===\n\n");

    es_solver_t* solver = es_solver_create();
    es_solver_add_charge(solver, (es_vec3_t){0.0, 0.0, 0.05}, 2.0e-6);
    es_solver_rebuild_images(solver);

    es_vec3_t p = {0.0, 0.0, 0.02};
    double v = es_solver_eval_potential(solver, p);

    printf("Потенціал у точці (0, 0, 0.02 м): %.4f кВ\n", v / 1000.0);

    es_solver_destroy(solver);
    return 0;
}
