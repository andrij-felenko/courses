#include <stdbool.h>
#include <math.h>

typedef struct {
    float x, y, z;
} Vec3;

static inline Vec3 v3_add(Vec3 a, Vec3 b) { return (Vec3){ a.x + b.x, a.y + b.y, a.z + b.z }; }
static inline Vec3 v3_sub(Vec3 a, Vec3 b) { return (Vec3){ a.x - b.x, a.y - b.y, a.z - b.z }; }
static inline Vec3 v3_neg(Vec3 a)         { return (Vec3){ -a.x, -a.y, -a.z }; }
static inline float v3_dot(Vec3 a, Vec3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }

static inline Vec3 v3_cross(Vec3 a, Vec3 b) {
    return (Vec3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

typedef struct {
    Vec3 points[4];
    int count;
} Simplex3D;

static inline void simplex3d_push(Simplex3D* s, Vec3 p) {
    s->points[3] = s->points[2];
    s->points[2] = s->points[1];
    s->points[1] = s->points[0];
    s->points[0] = p;
    if (s->count < 4) s->count++;
}

/* Обробка відрізка (2 точки) */
static inline bool solve_line(Simplex3D* s, Vec3* dir) {
    Vec3 a = s->points[0], b = s->points[1];
    Vec3 ab = v3_sub(b, a), ao = v3_neg(a);

    if (v3_dot(ab, ao) > 0.0f) {
        *dir = v3_cross(v3_cross(ab, ao), ab);
        if (v3_dot(*dir, *dir) < 1e-8f) {
            *dir = (fabsf(ab.x) > 0.9f) ? (Vec3){ 0, 1, 0 } : (Vec3){ 1, 0, 0 };
            *dir = v3_cross(ab, *dir);
        }
    } else {
        s->points[0] = a;
        s->count = 1;
        *dir = ao;
    }
    return false;
}

/* Обробка трикутника (3 точки) */
static inline bool solve_triangle(Simplex3D* s, Vec3* dir) {
    Vec3 a = s->points[0], b = s->points[1], c = s->points[2];
    Vec3 ab = v3_sub(b, a), ac = v3_sub(c, a), ao = v3_neg(a);
    Vec3 abc = v3_cross(ab, ac);

    Vec3 ab_perp = v3_cross(ab, abc);
    Vec3 ac_perp = v3_cross(abc, ac);

    if (v3_dot(ab_perp, ao) > 0.0f) {
        s->points[0] = a;
        s->points[1] = b;
        s->count = 2;
        return solve_line(s, dir);
    }
    if (v3_dot(ac_perp, ao) > 0.0f) {
        s->points[0] = a;
        s->points[1] = c;
        s->count = 2;
        return solve_line(s, dir);
    }

    if (v3_dot(abc, ao) > 0.0f) {
        *dir = abc;
    } else {
        s->points[1] = c;
        s->points[2] = b;
        *dir = v3_neg(abc);
    }
    return false;
}

/* Обробка тетраедра (4 точки) */
static inline bool solve_tetrahedron(Simplex3D* s, Vec3* dir) {
    Vec3 a = s->points[0], b = s->points[1], c = s->points[2], d = s->points[3];
    Vec3 ab = v3_sub(b, a), ac = v3_sub(c, a), ad = v3_sub(d, a), ao = v3_neg(a);

    Vec3 abc = v3_cross(ab, ac);
    Vec3 acd = v3_cross(ac, ad);
    Vec3 adb = v3_cross(ad, ab);

    if (v3_dot(abc, ao) > 0.0f) {
        s->points[0] = a; s->points[1] = b; s->points[2] = c;
        s->count = 3;
        return solve_triangle(s, dir);
    }
    if (v3_dot(acd, ao) > 0.0f) {
        s->points[0] = a; s->points[1] = c; s->points[2] = d;
        s->count = 3;
        return solve_triangle(s, dir);
    }
    if (v3_dot(adb, ao) > 0.0f) {
        s->points[0] = a; s->points[1] = d; s->points[2] = b;
        s->count = 3;
        return solve_triangle(s, dir);
    }

    /* Початок координат лежить усередині всіх чотирьох граней */
    return true;
}

static inline bool solve_simplex3d(Simplex3D* s, Vec3* dir) {
    if (s->count == 2) return solve_line(s, dir);
    if (s->count == 3) return solve_triangle(s, dir);
    if (s->count == 4) return solve_tetrahedron(s, dir);
    return false;
}

typedef Vec3 (*SupportFn3D)(const void* obj, Vec3 dir);

bool gjk_intersect_3d(const void* obj_a, SupportFn3D sup_a,
                      const void* obj_b, SupportFn3D sup_b) {
    Vec3 dir = { 0.0f, 1.0f, 0.0f };
    Vec3 p = v3_sub(sup_a(obj_a, dir), sup_b(obj_b, v3_neg(dir)));

    Simplex3D simplex = { .count = 0 };
    simplex3d_push(&simplex, p);
    dir = v3_neg(p);

    for (int iter = 0; iter < 40; ++iter) {
        if (v3_dot(dir, dir) < 1e-8f) return true;

        p = v3_sub(sup_a(obj_a, dir), sup_b(obj_b, v3_neg(dir)));
        if (v3_dot(p, dir) <= 0.0f) return false;

        simplex3d_push(&simplex, p);
        if (solve_simplex3d(&simplex, &dir)) return true;
    }
    return false;
}
