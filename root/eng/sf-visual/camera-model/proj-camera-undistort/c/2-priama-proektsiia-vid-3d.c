// Пряма проекція 3D точки простору на сенсор камери
bool project_point(const Point3D *pt_cam,
                   const CameraIntrinsics *K,
                   const DistortionCoeffs *D,
                   Point2D *out_pixel) {
    if (pt_cam->z <= 1e-6) {
        return false; // точка позаду або в площині оптичного центру
    }

    // 1. Нормовані координати
    double x = pt_cam->x / pt_cam->z;
    double y = pt_cam->y / pt_cam->z;

    // 2. Радіальна відстань
    double r2 = x * x + y * y;
    double r4 = r2 * r2;
    double r6 = r4 * r2;

    // 3. Радіальний і тангенціальний зсув
    double radial = 1.0 + D->k1 * r2 + D->k2 * r4 + D->k3 * r6;
    double dx_tangential = 2.0 * D->p1 * x * y + D->p2 * (r2 + 2.0 * x * x);
    double dy_tangential = D->p1 * (r2 + 2.0 * y * y) + 2.0 * D->p2 * x * y;

    double x_distorted = x * radial + dx_tangential;
    double y_distorted = y * radial + dy_tangential;

    // 4. Переведення в пікселі
    out_pixel->x = K->fx * x_distorted + K->cx;
    out_pixel->y = K->fy * y_distorted + K->cy;
    return true;
}
