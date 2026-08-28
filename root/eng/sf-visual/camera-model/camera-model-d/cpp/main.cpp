#include <cstdint>
#include <cmath>
#include <vector>
#include <span>
#include <memory>
#include <algorithm>

namespace vision {

struct CameraK {
    double fx{0.0}, fy{0.0};
    double cx{0.0}, cy{0.0};
};

struct Distortion {
    double k1{0.0}, k2{0.0}, k3{0.0};
    double p1{0.0}, p2{0.0};
};

struct Vec2d { double x{0.0}, y{0.0}; };
struct Vec3d { double x{0.0}, y{0.0}, z{0.0}; };

// Пряма проекція точки
[[nodiscard]] constexpr bool project_pinhole_distorted(const Vec3d& p_cam,
                                                       const CameraK& K,
                                                       const Distortion& D,
                                                       Vec2d& p_pix) noexcept {
    if (p_cam.z <= 1e-7) return false;

    const double x = p_cam.x / p_cam.z;
    const double y = p_cam.y / p_cam.z;

    const double r2 = x * x + y * y;
    const double r4 = r2 * r2;
    const double r6 = r4 * r2;

    const double radial = 1.0 + D.k1 * r2 + D.k2 * r4 + D.k3 * r6;
    const double dx_t = 2.0 * D.p1 * x * y + D.p2 * (r2 + 2.0 * x * x);
    const double dy_t = D.p1 * (r2 + 2.0 * y * y) + 2.0 * D.p2 * x * y;

    const double x_d = x * radial + dx_t;
    const double y_d = y * radial + dy_t;

    p_pix.x = K.fx * x_d + K.cx;
    p_pix.y = K.fy * y_d + K.cy;
    return true;
}

// Ітеративне розпрямлення
[[nodiscard]] Vec2d undistort_point_iterative(const Vec2d& dist_pix,
                                              const CameraK& K,
                                              const Distortion& D,
                                              int iters = 5) noexcept {
    const double x_d = (dist_pix.x - K.cx) / K.fx;
    const double y_d = (dist_pix.y - K.cy) / K.fy;
    double x = x_d, y = y_d;

    for (int i = 0; i < iters; ++i) {
        const double r2 = x * x + y * y;
        const double r4 = r2 * r2;
        const double r6 = r4 * r2;

        const double radial = 1.0 + D.k1 * r2 + D.k2 * r4 + D.k3 * r6;
        const double dx_t = 2.0 * D.p1 * x * y + D.p2 * (r2 + 2.0 * x * x);
        const double dy_t = D.p1 * (r2 + 2.0 * y * y) + 2.0 * D.p2 * x * y;

        x = (x_d - dx_t) / radial;
        y = (y_d - dy_t) / radial;
    }
    return Vec2d{x, y};
}

// Клас генерації карт та ремапу зображень
class CameraRectifier {
public:
    CameraRectifier(int w, int h, const CameraK& K_src, const Distortion& D, const CameraK& K_dst)
        : width_(w), height_(h), map_x_(w * h), map_y_(w * h) {
        for (int v_dst = 0; v_dst < h; ++v_dst) {
            for (int u_dst = 0; u_dst < w; ++u_dst) {
                const double x = (u_dst - K_dst.cx) / K_dst.fx;
                const double y = (v_dst - K_dst.cy) / K_dst.fy;

                const double r2 = x * x + y * y;
                const double r4 = r2 * r2;
                const double r6 = r4 * r2;

                const double radial = 1.0 + D.k1 * r2 + D.k2 * r4 + D.k3 * r6;
                const double dx_t = 2.0 * D.p1 * x * y + D.p2 * (r2 + 2.0 * x * x);
                const double dy_t = D.p1 * (r2 + 2.0 * y * y) + 2.0 * D.p2 * x * y;

                const double x_d = x * radial + dx_t;
                const double y_d = y * radial + dy_t;

                const int idx = v_dst * w + u_dst;
                map_x_[idx] = static_cast<float>(K_src.fx * x_d + K_src.cx);
                map_y_[idx] = static_cast<float>(K_src.fy * y_d + K_src.cy);
            }
        }
    }

    void process(std::span<const uint8_t> src, std::span<uint8_t> dst) const noexcept {
        for (int y = 0; y < height_; ++y) {
            for (int x = 0; x < width_; ++x) {
                const int idx = y * width_ + x;
                const float sx = map_x_[idx];
                const float sy = map_y_[idx];

                const int x0 = static_cast<int>(std::floor(sx));
                const int y0 = static_cast<int>(std::floor(sy));
                const int x1 = x0 + 1;
                const int y1 = y0 + 1;

                if (x0 >= 0 && x1 < width_ && y0 >= 0 && y1 < height_) {
                    const float fx_val = sx - static_cast<float>(x0);
                    const float fy_val = sy - static_cast<float>(y0);

                    const float p00 = static_cast<float>(src[y0 * width_ + x0]);
                    const float p01 = static_cast<float>(src[y0 * width_ + x1]);
                    const float p10 = static_cast<float>(src[y1 * width_ + x0]);
                    const float p11 = static_cast<float>(src[y1 * width_ + x1]);

                    const float val = (p00 * (1.0f - fx_val) + p01 * fx_val) * (1.0f - fy_val) +
                                      (p10 * (1.0f - fx_val) + p11 * fx_val) * fy_val;

                    dst[idx] = static_cast<uint8_t>(std::clamp(val + 0.5f, 0.0f, 255.0f));
                } else {
                    dst[idx] = 0;
                }
            }
        }
    }

private:
    int width_{0}, height_{0};
    std::vector<float> map_x_, map_y_;
};

} // namespace vision
