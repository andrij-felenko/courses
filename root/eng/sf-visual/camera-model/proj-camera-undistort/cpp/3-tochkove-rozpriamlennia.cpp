namespace vision {

// Ітеративне розпрямлення однієї точки
[[nodiscard]] Point2D undistort_point(const Point2D& dist_pixel,
                                      const CameraIntrinsics& K,
                                      const DistortionCoeffs& D,
                                      int max_iters = 5) noexcept {
    const double x_d = (dist_pixel.x - K.cx) / K.fx;
    const double y_d = (dist_pixel.y - K.cy) / K.fy;

    double x = x_d;
    double y = y_d;

    for (int i = 0; i < max_iters; ++i) {
        const double r2 = x * x + y * y;
        const double r4 = r2 * r2;
        const double r6 = r4 * r2;

        const double radial = 1.0 + D.k1 * r2 + D.k2 * r4 + D.k3 * r6;
        const double dx_tan = 2.0 * D.p1 * x * y + D.p2 * (r2 + 2.0 * x * x);
        const double dy_tan = D.p1 * (r2 + 2.0 * y * y) + 2.0 * D.p2 * x * y;

        x = (x_d - dx_tan) / radial;
        y = (y_d - dy_tan) / radial;
    }

    return Point2D{x, y};
}

} // namespace vision
