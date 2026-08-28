/* C Implementation: Lambertian Diffuse Lighting and Monte Carlo Sampling */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    double r, g, b;
} ColorRGB;

/* Векторні операції */
static inline Vec3 vec3_create(double x, double y, double z) {
    Vec3 v = {x, y, z};
    return v;
}

static inline double vec3_dot(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline Vec3 vec3_normalize(Vec3 v) {
    double len = sqrt(vec3_dot(v, v));
    if (len < 1e-12) return vec3_create(0, 0, 0);
    return vec3_create(v.x / len, v.y / len, v.z / len);
}

static inline Vec3 vec3_scale(Vec3 v, double s) {
    return vec3_create(v.x * s, v.y * s, v.z * s);
}

/* Обчислення ламбертової BRDF */
double lambert_brdf(double albedo) {
    return albedo / M_PI;
}

/* Ламбертів шейдинг для одного джерела світла */
ColorRGB compute_lambert_shading(Vec3 point, Vec3 normal, Vec3 light_pos,
                                ColorRGB light_intensity, ColorRGB surface_albedo) {
    /* Вектор напрямку на джерело світла */
    Vec3 light_dir = vec3_create(light_pos.x - point.x,
                                 light_pos.y - point.y,
                                 light_pos.z - point.z);
    double dist_sq = vec3_dot(light_dir, light_dir);
    Vec3 L = vec3_normalize(light_dir);
    Vec3 N = vec3_normalize(normal);

    /* Косинус кута падіння (скалярний добуток) */
    double NdotL = vec3_dot(N, L);
    if (NdotL < 0.0) NdotL = 0.0; /* Затінений бок */

    /* Розрахунок згасання за законами обернених квадратів */
    double attenuation = 1.0 / (dist_sq + 1e-6);

    /* Відбитий колір для кожного спектрального каналу (R, G, B) */
    ColorRGB result;
    result.r = light_intensity.r * (surface_albedo.r / M_PI) * NdotL * attenuation;
    result.g = light_intensity.g * (surface_albedo.g / M_PI) * NdotL * attenuation;
    result.b = light_intensity.b * (surface_albedo.b / M_PI) * NdotL * attenuation;

    return result;
}

/* Генерація косинусно-зваженого напрямку для Ray Tracing (Монте-Карло) */
Vec3 sample_hemisphere_cosine(Vec3 N, double u1, double u2) {
    /* Рівномірний розподіл у полярних координатах */
    double r = sqrt(u1);
    double phi = 2.0 * M_PI * u2;

    /* Декартові координати у локальному просторі з нормаллю вздовж Z */
    double x = r * cos(phi);
    double y = r * sin(phi);
    double z = sqrt(fmax(0.0, 1.0 - u1));

    /* Побудова ортонормованого базису (Tangent, Bitangent, Normal) */
    Vec3 up = (fabs(N.z) < 0.999) ? vec3_create(0, 0, 1) : vec3_create(1, 0, 0);
    Vec3 T = vec3_normalize(vec3_create(up.y * N.z - up.z * N.y,
                                        up.z * N.x - up.x * N.z,
                                        up.x * N.y - up.y * N.x));
    Vec3 B = vec3_create(N.y * T.z - N.z * T.y,
                         N.z * T.x - N.x * T.z,
                         N.x * T.y - N.y * T.x);

    /* Трансформація в глобальну систему координат */
    Vec3 dir;
    dir.x = T.x * x + B.x * y + N.x * z;
    dir.y = T.y * x + B.y * y + N.y * z;
    dir.z = T.z * x + B.z * y + N.z * z;

    return vec3_normalize(dir);
}

int main(void) {
    Vec3 surface_point = {0.0, 0.0, 0.0};
    Vec3 surface_normal = {0.0, 0.0, 1.0};
    Vec3 light_position = {2.0, 2.0, 3.0};

    ColorRGB light = {100.0, 100.0, 100.0}; /* Потужне джерело */
    ColorRGB albedo = {0.8, 0.8, 0.8};       /* Білий матовий матеріал */

    ColorRGB out_color = compute_lambert_shading(surface_point, surface_normal,
                                                light_position, light, albedo);

    printf("Lambert Diffuse Color: R=%.4f, G=%.4f, B=%.4f\n",
           out_color.r, out_color.g, out_color.b);
    return 0;
}
