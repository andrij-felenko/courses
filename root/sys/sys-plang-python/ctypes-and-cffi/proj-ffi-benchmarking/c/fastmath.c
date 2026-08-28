// fastmath.c
#include <stdint.h>
#include <stddef.h>

#if defined(_WIN32)
  #define EXPORT_API __declspec(dllexport)
#else
  #define EXPORT_API __attribute__((visibility("default")))
#endif

typedef struct {
    double x;
    double y;
    double z;
    uint32_t id;
} Point3D;

EXPORT_API uint32_t fast_crc32_step(uint32_t crc, uint8_t byte) {
    crc ^= byte;
    for (int i = 0; i < 8; ++i) {
        crc = (crc >> 1) ^ (0xEDB88320u & (-(crc & 1u)));
    }
    return crc;
}

EXPORT_API void vector_scale(double *data, size_t size, double factor) {
    for (size_t i = 0; i < size; ++i) {
        data[i] *= factor;
    }
}

EXPORT_API void transform_point(Point3D *pt, double dx, double dy, double dz) {
    if (!pt) return;
    pt->x += dx;
    pt->y += dy;
    pt->z += dz;
    pt->id += 1;
}
