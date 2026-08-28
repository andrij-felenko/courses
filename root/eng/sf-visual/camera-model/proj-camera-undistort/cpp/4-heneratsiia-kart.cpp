namespace vision {

class ImageRemapper {
public:
    ImageRemapper(int width, int height,
                  const CameraIntrinsics& K_src,
                  const DistortionCoeffs& D,
                  const CameraIntrinsics& K_dst)
        : width_(width), height_(height),
          map_x_(width * height), map_y_(width * height) {
        build_lut(K_src, D, K_dst);
    }

    [[nodiscard]] int width() const noexcept { return width_; }
    [[nodiscard]] int height() const noexcept { return height_; }
    [[nodiscard]] std::span<const float> map_x() const noexcept { return map_x_; }
    [[nodiscard]] std::span<const float> map_y() const noexcept { return map_y_; }

private:
    int width_{0};
    int height_{0};
    std::vector<float> map_x_;
    std::vector<float> map_y_;

    void build_lut(const CameraIntrinsics& K_src,
                   const DistortionCoeffs& D,
                   const CameraIntrinsics& K_dst) {
        for (int v_dst = 0; v_dst < height_; ++v_dst) {
            for (int u_dst = 0; u_dst < width_; ++u_dst) {
                const double x = (u_dst - K_dst.cx) / K_dst.fx;
                const double y = (v_dst - K_dst.cy) / K_dst.fy;

                const double r2 = x * x + y * y;
                const double r4 = r2 * r2;
                const double r6 = r4 * r2;

                const double radial = 1.0 + D.k1 * r2 + D.k2 * r4 + D.k3 * r6;
                const double dx_tan = 2.0 * D.p1 * x * y + D.p2 * (r2 + 2.0 * x * x);
                const double dy_tan = D.p1 * (r2 + 2.0 * y * y) + 2.0 * D.p2 * x * y;

                const double x_d = x * radial + dx_tan;
                const double y_d = y * radial + dy_tan;

                const auto u_src = static_cast<float>(K_src.fx * x_d + K_src.cx);
                const auto v_src = static_cast<float>(K_src.fy * y_d + K_src.cy);

                const int idx = v_dst * width_ + u_dst;
                map_x_[idx] = u_src;
                map_y_[idx] = v_src;
            }
        }
    }
};

} // namespace vision
