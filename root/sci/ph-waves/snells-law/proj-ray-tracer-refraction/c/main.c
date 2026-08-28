#include <math.h>
#include <stdbool.h>

typedef struct {
    double x;
    double y;
    double z;
} Vector3;

static inline double vec3_dot(Vector3 a, Vector3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline Vector3 vec3_add(Vector3 a, Vector3 b) {
    return (Vector3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vector3 vec3_scale(Vector3 v, double s) {
    return (Vector3){v.x * s, v.y * s, v.z * s};
}

/*
 * Обчислює напрямок заломленого променя за законом Снелла у 3D.
 * I — нормований вектор падаючого променя (спрямований в точку падіння).
 * N — нормований вектор нормалі поверхні.
 * eta — відношення n1 / n2.
 * out_refracted — вказівник на вектор заломлення T (якщо є).
 * Повертає true якщо заломлення відбулося, або false при повному внутрішньому відбитті.
 */
bool ray_refract(Vector3 I, Vector3 N, double eta, Vector3* out_refracted) {
    double cos_i = -vec3_dot(I, N);
    Vector3 oriented_N = N;

    /* Перевіряємо, з якого боку межі входить промінь */
    if (cos_i < 0.0) {
        cos_i = -cos_i;
        oriented_N = vec3_scale(N, -1.0);
    }

    double k = 1.0 - eta * eta * (1.0 - cos_i * cos_i);
    if (k < 0.0) {
        /* Повне внутрішнє відбиття */
        return false;
    }

    double cos_t = sqrt(k);
    Vector3 term1 = vec3_scale(I, eta);
    Vector3 term2 = vec3_scale(oriented_N, eta * cos_i - cos_t);
    *out_refracted = vec3_add(term1, term2);

    return true;
}
