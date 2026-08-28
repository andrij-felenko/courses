#include <math.h>

typedef struct { float x, y; } Vec2;

float dot(Vec2 a, Vec2 b) {        /* скалярний добуток */
    return a.x * b.x + a.y * b.y;
}

float magnitude(Vec2 a) {          /* довжина = корінь з a·a */
    return sqrtf(dot(a, a));
}

/* кут між векторами у радіанах, чверть-незалежно */
float angle_between(Vec2 a, Vec2 b) {
    float c = dot(a, b) / (magnitude(a) * magnitude(b));
    if (c >  1.0f) c =  1.0f;      /* затиск проти похибки округлення */
    if (c < -1.0f) c = -1.0f;      /* інакше acosf поверне NaN */
    return acosf(c);
}
