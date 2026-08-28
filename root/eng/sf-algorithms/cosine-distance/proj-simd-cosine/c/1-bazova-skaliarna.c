#include <math.h>
#include <stddef.h>
#include <stdbool.h>

typedef struct {
    float distance;
    bool success;
} MetricResult;

MetricResult cosine_distance_scalar(const float *u, const float *v, size_t size) {
    MetricResult res = {1.0f, false};
    if (!u || !v || size == 0) {
        return res;
    }

    float dot = 0.0f;
    float sq_u = 0.0f;
    float sq_v = 0.0f;

    // Скалярний прохід із розгортанням циклу на 4 елементи
    size_t i = 0;
    for (; i + 3 < size; i += 4) {
        float u0 = u[i], u1 = u[i+1], u2 = u[i+2], u3 = u[i+3];
        float v0 = v[i], v1 = v[i+1], v2 = v[i+2], v3 = v[i+3];

        dot  += u0 * v0 + u1 * v1 + u2 * v2 + u3 * v3;
        sq_u += u0 * u0 + u1 * u1 + u2 * u2 + u3 * u3;
        sq_v += v0 * v0 + v1 * v1 + v2 * v2 + v3 * v3;
    }

    // Залишок циклу
    for (; i < size; ++i) {
        float ui = u[i];
        float vi = v[i];
        dot  += ui * vi;
        sq_u += ui * ui;
        sq_v += vi * vi;
    }

    // Захист від ділення на нуль (нульові вектори)
    const float eps = 1e-12f;
    if (sq_u < eps || sq_v < eps) {
        return res; // Повертаємо 1.0 за замовчуванням при невизначеності
    }

    float norm_product = sqrtf(sq_u) * sqrtf(sq_v);
    float cos_sim = dot / norm_product;

    // Обрізання меж для захисту від плаваючої похибки (наприклад, 1.0000001)
    if (cos_sim > 1.0f) cos_sim = 1.0f;
    if (cos_sim < -1.0f) cos_sim = -1.0f;

    res.distance = 1.0f - cos_sim;
    res.success = true;
    return res;
}
