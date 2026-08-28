#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x;
    double y;
    double z;
} Vector3;

static inline Vector3 vec_add(Vector3 a, Vector3 b) {
    return (Vector3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vector3 vec_sub(Vector3 a, Vector3 b) {
    return (Vector3){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vector3 vec_scale(Vector3 v, double s) {
    return (Vector3){v.x * s, v.y * s, v.z * s};
}

static inline Vector3 vec_cross(Vector3 a, Vector3 b) {
    return (Vector3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline double vec_length(Vector3 v) {
    return sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
}

Vector3 compute_biot_savart(const Vector3* nodes, size_t count, double current, Vector3 point) {
    const double mu0 = 4.0 * M_PI * 1e-7;
    const double factor = (mu0 * current) / (4.0 * M_PI);
    Vector3 B = {0.0, 0.0, 0.0};

    for (size_t i = 0; i < count - 1; ++i) {
        Vector3 dl = vec_sub(nodes[i + 1], nodes[i]);
        Vector3 r_mid = vec_scale(vec_add(nodes[i], nodes[i + 1]), 0.5);
        Vector3 R = vec_sub(point, r_mid);
        double dist = vec_length(R);

        if (dist < 1e-9) continue;

        double dist3 = dist * dist * dist;
        Vector3 dB = vec_scale(vec_cross(dl, R), factor / dist3);
        B = vec_add(B, dB);
    }
    return B;
}

int main(void) {
    const double radius = 0.1;
    const int segments = 2000;
    const double current = 10.0;

    Vector3* loop = (Vector3*)malloc((segments + 1) * sizeof(Vector3));
    if (!loop) return 1;

    for (int i = 0; i <= segments; ++i) {
        double phi = 2.0 * M_PI * i / segments;
        loop[i] = (Vector3){radius * cos(phi), radius * sin(phi), 0.0};
    }

    Vector3 point = {0.0, 0.0, 0.05};
    Vector3 B = compute_biot_savart(loop, segments + 1, current, point);

    printf("--- Результати чисельного розрахунку (C) ---\n");
    printf("B_x: %.4f uT\n", B.x * 1e6);
    printf("B_y: %.4f uT\n", B.y * 1e6);
    printf("B_z: %.4f uT (Очікуване: ~44.9639 uT)\n", B.z * 1e6);

    free(loop);
    return 0;
}
