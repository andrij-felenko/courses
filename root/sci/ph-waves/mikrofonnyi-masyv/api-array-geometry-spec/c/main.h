#ifndef ARRAY_GEOMETRY_SPEC_H
#define ARRAY_GEOMETRY_SPEC_H

#include <stddef.h>

#define MAX_ARRAY_MICS 32

typedef enum {
    TOPOLOGY_1D_LINEAR,
    TOPOLOGY_2D_CIRCULAR,
    TOPOLOGY_2D_PLANAR,
    TOPOLOGY_3D_SPHERICAL,
    TOPOLOGY_CUSTOM
} ArrayTopologyType;

typedef struct {
    float x; // координата X у метрах
    float y; // координата Y у метрах
    float z; // координата Z у метрах
} Vec3;

typedef struct {
    ArrayTopologyType type;
    size_t num_mics;
    Vec3 positions[MAX_ARRAY_MICS];
    float sound_speed;      // швидкість звуку c (м/с), за замовчуванням 343.0
    float sampling_rate;    // частота дискретизації fs (Гц)
    float min_spacing;      // мінімальна відстань між капсулями (м)
    float max_frequency_hz; // гранична частота f_alias без просторового аліасингу
} ArrayGeometryConfig;

typedef struct {
    float azimuth_deg;   // азимут [-180, +180] або [-90, +90]
    float elevation_deg; // кут місця [-90, +90]
    float delays_sec[MAX_ARRAY_MICS];
    float weights[MAX_ARRAY_MICS];
} SteeringVectorConfig;

// Ініціалізація 1D лінійного масиву
void init_linear_array(ArrayGeometryConfig* cfg, size_t num_mics, float spacing_m, float fs);

// Ініціалізація 2D кільцевого масиву
void init_circular_array(ArrayGeometryConfig* cfg, size_t num_mics, float radius_m, float fs);

// Розрахунок затримок та ваг для заданого кутового напрямку
void compute_steering_vector(const ArrayGeometryConfig* cfg, float azimuth_deg, float elevation_deg, SteeringVectorConfig* out);

#endif // ARRAY_GEOMETRY_SPEC_H
