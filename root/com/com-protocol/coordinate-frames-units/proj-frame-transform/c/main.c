#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define M_PI_F 3.14159265358979323846f
#define DEG_TO_RAD_F (M_PI_F / 180.0f)
#define RAD_TO_DEG_F (180.0f / M_PI_F)

/* Константи референц-еліпсоїда WGS84 */
#define WGS84_A 6378137.0                /* Велика піввісь (метри) */
#define WGS84_F (1.0 / 298.257223563)        /* Стиснення еліпсоїда */
#define WGS84_E2 (2.0 * WGS84_F - WGS84_F * WGS84_F) /* Квадрат ексцентриситету */

typedef struct {
    float x;
    float y;
    float z;
} vector3f_t;

typedef struct {
    double lat; /* Широта у градусах WGS84 */
    double lon; /* Довгота у градусах WGS84 */
    double alt; /* Висота над рівнем моря AMSL (метри) */
} geodetic_coord_t;

typedef struct {
    float w;
    float x;
    float y;
    float z;
} quaternion_t;

/* 1. Локальні декартові базиси: NED <-> ENU */
static inline vector3f_t transform_ned_to_enu(vector3f_t ned) {
    vector3f_t enu;
    enu.x =  ned.y;
    enu.y =  ned.x;
    enu.z = -ned.z;
    return enu;
}

static inline vector3f_t transform_enu_to_ned(vector3f_t enu) {
    vector3f_t ned;
    ned.x =  enu.y;
    ned.y =  enu.x;
    ned.z = -enu.z;
    return ned;
}

/* 2. Зв'язані базиси корпусу: Body FRD <-> Body FLU */
static inline vector3f_t transform_body_frd_to_flu(vector3f_t frd) {
    vector3f_t flu;
    flu.x =  frd.x;
    flu.y = -frd.y;
    flu.z = -frd.z;
    return flu;
}

static inline vector3f_t transform_body_flu_to_frd(vector3f_t flu) {
    vector3f_t frd;
    frd.x =  flu.x;
    frd.y = -flu.y;
    frd.z = -flu.z;
    return frd;
}

/* Нормалізація різниці кутів довготи через лінію зміни дат */
static inline double normalize_angle_rad(double angle) {
    while (angle > M_PI_F)  angle -= 2.0 * M_PI_F;
    while (angle < -M_PI_F) angle += 2.0 * M_PI_F;
    return angle;
}

/* 3. Проєкція геодезичних координат WGS84 у локальний базис NED */
vector3f_t geodetic_to_local_ned(geodetic_coord_t point, geodetic_coord_t home) {
    double phi_0 = home.lat * (double)DEG_TO_RAD_F;
    double sin_phi = sin(phi_0);
    double cos_phi = cos(phi_0);
    
    double d_phi = (point.lat - home.lat) * (double)DEG_TO_RAD_F;
    double d_lambda = (point.lon - home.lon) * (double)DEG_TO_RAD_F;
    d_lambda = normalize_angle_rad(d_lambda);

    /* Радіуси кривини еліпсоїда на широті точки Home */
    double denom = 1.0 - WGS84_E2 * sin_phi * sin_phi;
    double sqrt_denom = sqrt(denom);
    double m = (WGS84_A * (1.0 - WGS84_E2)) / (denom * sqrt_denom); /* Меридіан (Північ) */
    double n = WGS84_A / sqrt_denom;                                /* Перший вертикал (Схід) */

    vector3f_t ned;
    ned.x = (float)(d_phi * (m + home.alt));
    ned.y = (float)(d_lambda * (n + home.alt) * cos_phi);
    ned.z = (float)(-(point.alt - home.alt));
    return ned;
}

/* Нормалізація кватерніона з перевіркою на нульову норму */
quaternion_t quaternion_normalize(quaternion_t q) {
    float norm_sq = q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z;
    if (norm_sq < 1e-12f) {
        quaternion_t id = {1.0f, 0.0f, 0.0f, 0.0f};
        return id;
    }
    float inv_norm = 1.0f / sqrtf(norm_sq);
    quaternion_t res = {q.w * inv_norm, q.x * inv_norm, q.y * inv_norm, q.z * inv_norm};
    return res;
}

/* 4. Швидкий поворот вектора кватерніоном за формулою Родрігеса */
vector3f_t quaternion_rotate_vector(quaternion_t q, vector3f_t v) {
    /* t = 2 * (q_v x v) */
    float tx = 2.0f * (q.y * v.z - q.z * v.y);
    float ty = 2.0f * (q.z * v.x - q.x * v.z);
    float tz = 2.0f * (q.x * v.y - q.y * v.x);

    /* v_rot = v + w * t + (q_v x t) */
    vector3f_t res;
    res.x = v.x + q.w * tx + (q.y * tz - q.z * ty);
    res.y = v.y + q.w * ty + (q.z * tx - q.x * tz);
    res.z = v.z + q.w * tz + (q.x * ty - q.y * tx);
    return res;
}
