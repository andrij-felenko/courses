// fastmath.cpp
#include <cstdint>
#include <cstddef>
#include <span>

#if defined(_WIN32)
  #define EXPORT_API extern "C" __declspec(dllexport)
#else
  #define EXPORT_API extern "C" __attribute__((visibility("default")))
#endif

struct Point3D {
    double x;
    double y;
    double z;
    std::uint32_t id;
};

EXPORT_API std::uint32_t fast_crc32_step(std::uint32_t crc, std::uint8_t byte) noexcept {
    crc ^= byte;
    for (int i = 0; i < 8; ++i) {
        crc = (crc >> 1) ^ (0xEDB88320u & (-(crc & 1u)));
    }
    return crc;
}

EXPORT_API void vector_scale(double *data, std::size_t size, double factor) noexcept {
    if (!data) return;
    std::span<double> span_data(data, size);
    for (auto &val : span_data) {
        val *= factor;
    }
}

EXPORT_API void transform_point(Point3D *pt, double dx, double dy, double dz) noexcept {
    if (!pt) return;
    pt->x += dx;
    pt->y += dy;
    pt->z += dz;
    pt->id += 1;
}
