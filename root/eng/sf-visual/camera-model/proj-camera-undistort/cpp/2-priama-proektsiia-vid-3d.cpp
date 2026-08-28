namespace vision {

// Пряма проекція 3D точки камери на сенсор
[[nodiscard]] constexpr bool project_point(const Point3D& pt_cam,
                                           const CameraIntrinsics& K,
                                           const DistortionCoeffs& D,
                                           Point2D& out_pixel) noexcept {
    if (pt_cam.z <= 1e-6) {
        return false;
    }

    const double x = pt_cam.x / pt_cam.z;
    const double y = pt_cam.y / pt_cam.z;

    const double r2 = x * x + y * y;
    const double r4 = r2 * r2;
    const double r6 = r4 * r2;

    const double radial = 1.0 + D.k1 * r2 + D.k2 * r4 + D.k3 * r6;
    const double dx_tangential = 2.0 * D.p1 * x * y + D.p2 * (r2 + 2.0 * x * x);
    const double dy_tangential = D.p1 * (r2 + 2.0 * y * y) + 2.0 * D.p2 * x * y;

    const double x_dist = x * radial + dx_tangential;
    const double y_dist = y * radial + dy_tangential;

    out_pixel.x = K.fx * x_dist + K.cx;
    out_pixel.y = K.fy * y_dist + K.cy;
    return true;
}

} // namespace vision
