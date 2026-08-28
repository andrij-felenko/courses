#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h>

typedef struct {
    double fx, fy;
    double cx, cy;
} CameraK;

typedef struct {
    double k1, k2, k3;
    double p1, p2;
} Distortion;

typedef struct {
    double x, y;
} Vec2d;

typedef struct {
    double x, y, z;
} Vec3d;

// Пряма проекція 3D точки на сенсор
bool project_pinhole_distorted(const Vec3d *p_cam, const CameraK *K,
                               const Distortion *D, Vec2d *p_pix) {
    if (p_cam->z <= 1e-7) return false;

    double x = p_cam->x / p_cam->z;
    double y = p_cam->y / p_cam->z;

    double r2 = x * x + y * y;
    double r4 = r2 * r2;
    double r6 = r4 * r2;

    double radial = 1.0 + D->k1 * r2 + D->k2 * r4 + D->k3 * r6;
    double dx_t = 2.0 * D->p1 * x * y + D->p2 * (r2 + 2.0 * x * x);
    double dy_t = D->p1 * (r2 + 2.0 * y * y) + 2.0 * D->p2 * x * y;

    double x_d = x * radial + dx_t;
    double y_d = y * radial + dy_t;

    p_pix->x = K->fx * x_d + K->cx;
    p_pix->y = K->fy * y_d + K->cy;
    return true;
}

// Ітеративне розпрямлення однієї точки
Vec2d undistort_point_iterative(const Vec2d *dist_pix, const CameraK *K,
                                const Distortion *D, int iters) {
    double x_d = (dist_pix->x - K->cx) / K->fx;
    double y_d = (dist_pix->y - K->cy) / K->fy;
    double x = x_d, y = y_d;

    for (int i = 0; i < iters; ++i) {
        double r2 = x * x + y * y;
        double r4 = r2 * r2;
        double r6 = r4 * r2;

        double radial = 1.0 + D->k1 * r2 + D->k2 * r4 + D->k3 * r6;
        double dx_t = 2.0 * D->p1 * x * y + D->p2 * (r2 + 2.0 * x * x);
        double dy_t = D->p1 * (r2 + 2.0 * y * y) + 2.0 * D->p2 * x * y;

        x = (x_d - dx_t) / radial;
        y = (y_d - dy_t) / radial;
    }
    Vec2d norm_pt = { x, y };
    return norm_pt;
}

// Білінійний ремап сірого зображення
void remap_image_bilinear(const uint8_t *src, int w, int h,
                          const float *map_x, const float *map_y, uint8_t *dst) {
    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            int idx = y * w + x;
            float sx = map_x[idx];
            float sy = map_y[idx];

            int x0 = (int)floorf(sx);
            int y0 = (int)floorf(sy);
            int x1 = x0 + 1;
            int y1 = y0 + 1;

            if (x0 >= 0 && x1 < w && y0 >= 0 && y1 < h) {
                float fx_val = sx - (float)x0;
                float fy_val = sy - (float)y0;

                float p00 = (float)src[y0 * w + x0];
                float p01 = (float)src[y0 * w + x1];
                float p10 = (float)src[y1 * w + x0];
                float p11 = (float)src[y1 * w + x1];

                float val = (p00 * (1.0f - fx_val) + p01 * fx_val) * (1.0f - fy_val) +
                            (p10 * (1.0f - fx_val) + p11 * fx_val) * fy_val;

                dst[idx] = (uint8_t)(val + 0.5f);
            } else {
                dst[idx] = 0;
            }
        }
    }
}
