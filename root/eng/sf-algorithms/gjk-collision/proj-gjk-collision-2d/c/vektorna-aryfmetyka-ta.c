#include <stdbool.h>
#include <stdio.h>
#include <math.h>

typedef struct {
    float x;
    float y;
} Vec2;

static inline Vec2 vec2_create(float x, float y) {
    return (Vec2){ x, y };
}

static inline Vec2 vec2_add(Vec2 a, Vec2 b) {
    return (Vec2){ a.x + b.x, a.y + b.y };
}

static inline Vec2 vec2_sub(Vec2 a, Vec2 b) {
    return (Vec2){ a.x - b.x, a.y - b.y };
}

static inline Vec2 vec2_neg(Vec2 a) {
    return (Vec2){ -a.x, -a.y };
}

static inline float vec2_dot(Vec2 a, Vec2 b) {
    return a.x * b.x + a.y * b.y;
}

static inline float vec2_cross(Vec2 a, Vec2 b) {
    return a.x * b.y - a.y * b.x;
}

/* Потрійний векторний добуток у 2D: (a × b) × c */
static inline Vec2 vec2_triple_product(Vec2 a, Vec2 b, Vec2 c) {
    float z = a.x * b.y - a.y * b.x;
    return (Vec2){ -c.y * z, c.x * z };
}

/* Опорна точка для опуклого многокутника */
Vec2 polygon_support(const Vec2* vertices, int count, Vec2 dir) {
    int best_index = 0;
    float max_dot = vec2_dot(vertices[0], dir);

    for (int i = 1; i < count; ++i) {
        float dot = vec2_dot(vertices[i], dir);
        if (dot > max_dot) {
            max_dot = dot;
            best_index = i;
        }
    }
    return vertices[best_index];
}

/* Опорна точка для кола (аналітична формула) */
Vec2 circle_support(Vec2 center, float radius, Vec2 dir) {
    float len_sq = vec2_dot(dir, dir);
    if (len_sq < 1e-8f) {
        return center;
    }
    float inv_len = radius / sqrtf(len_sq);
    return (Vec2){ center.x + dir.x * inv_len, center.y + dir.y * inv_len };
}
