#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define M_PI_VAL 3.14159265358979323846

typedef struct {
    double x, y, z;
} Vector3;

static inline Vector3 vec_add(Vector3 a, Vector3 b) {
    return (Vector3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vector3 vec_scale(Vector3 a, double s) {
    return (Vector3){a.x * s, a.y * s, a.z * s};
}

static inline double vec_dot(Vector3 a, Vector3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline Vector3 vec_cross(Vector3 a, Vector3 b) {
    return (Vector3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline double vec_norm(Vector3 a) {
    return sqrt(vec_dot(a, a));
}

typedef struct {
    Vector3 b1, b2, b3;
    double v_cell;
} ReciprocalLatticeC;

bool reciprocal_lattice_init(ReciprocalLatticeC *lat, Vector3 a1, Vector3 a2, Vector3 a3) {
    Vector3 cross23 = vec_cross(a2, a3);
    lat->v_cell = vec_dot(a1, cross23);
    if (fabs(lat->v_cell) < 1e-12) {
        return false; // Помилка: компланарні вектори
    }
    double factor = 2.0 * M_PI_VAL / lat->v_cell;
    lat->b1 = vec_scale(cross23, factor);
    lat->b2 = vec_scale(vec_cross(a3, a1), factor);
    lat->b3 = vec_scale(vec_cross(a1, a2), factor);
    return true;
}

Vector3 reciprocal_get_g(const ReciprocalLatticeC *lat, int h, int k, int l) {
    Vector3 gh = vec_scale(lat->b1, (double)h);
    Vector3 gk = vec_scale(lat->b2, (double)k);
    Vector3 gl = vec_scale(lat->b3, (double)l);
    return vec_add(vec_add(gh, gk), gl);
}

double reciprocal_interplanar_spacing(const ReciprocalLatticeC *lat, int h, int k, int l) {
    Vector3 g = reciprocal_get_g(lat, h, k, l);
    double g_len = vec_norm(g);
    if (g_len < 1e-12) return -1.0;
    return 2.0 * M_PI_VAL / g_len;
}

bool reciprocal_is_inside_bz(const ReciprocalLatticeC *lat, Vector3 k_vec, int max_index) {
    for (int h = -max_index; h <= max_index; ++h) {
        for (int k = -max_index; k <= max_index; ++k) {
            for (int l = -max_index; l <= max_index; ++l) {
                if (h == 0 && k == 0 && l == 0) continue;
                Vector3 g = reciprocal_get_g(lat, h, k, l);
                double g_sq = vec_dot(g, g);
                if (vec_dot(k_vec, g) > 0.5 * g_sq + 1e-9) {
                    return false;
                }
            }
        }
    }
    return true;
}

int main(void) {
    double a = 0.543; // Parameter in nm
    Vector3 a1 = {0.0, a / 2.0, a / 2.0};
    Vector3 a2 = {a / 2.0, 0.0, a / 2.0};
    Vector3 a3 = {a / 2.0, a / 2.0, 0.0};

    ReciprocalLatticeC lat;
    if (!reciprocal_lattice_init(&lat, a1, a2, a3)) {
        printf("Помилка ініціалізації базису!\n");
        return 1;
    }

    printf("Об'єм V_cell (C): %.5f nm^3\n", lat.v_cell);
    printf("Міжплощинна відстань d(111): %.5f nm\n", reciprocal_interplanar_spacing(&lat, 1, 1, 1));
    printf("Міжплощинна відстань d(220): %.5f nm\n", reciprocal_interplanar_spacing(&lat, 2, 2, 0));

    Vector3 k_gamma = {0.0, 0.0, 0.0};
    Vector3 k_outside = vec_scale(lat.b1, 0.8);

    printf("Gamma у ЗБ: %s\n", reciprocal_is_inside_bz(&lat, k_gamma, 2) ? "так" : "ні");
    printf("k_outside у ЗБ: %s\n", reciprocal_is_inside_bz(&lat, k_outside, 2) ? "так" : "ні");
    return 0;
}
