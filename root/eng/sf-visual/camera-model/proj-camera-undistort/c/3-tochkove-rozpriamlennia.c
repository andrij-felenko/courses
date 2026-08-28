// Інверсія дисторсії для одиничного пікселя
Point2D undistort_point(const Point2D *distorted_pixel,
                        const CameraIntrinsics *K,
                        const DistortionCoeffs *D) {
    // 1. Початкове наближення в нормованих координатах
    double x_d = (distorted_pixel->x - K->cx) / K->fx;
    double y_d = (distorted_pixel->y - K->cy) / K->fy;

    double x = x_d;
    double y = y_d;

    // 2. Ітерації фіксованої точки
    for (int iter = 0; iter < 5; ++iter) {
        double r2 = x * x + y * y;
        double r4 = r2 * r2;
        double r6 = r4 * r2;

        double radial = 1.0 + D->k1 * r2 + D->k2 * r4 + D->k3 * r6;
        double dx_tan = 2.0 * D->p1 * x * y + D->p2 * (r2 + 2.0 * x * x);
        double dy_tan = D->p1 * (r2 + 2.0 * y * y) + 2.0 * D->p2 * x * y;

        // Поправка кроку
        x = (x_d - dx_tan) / radial;
        y = (y_d - dy_tan) / radial;
    }

    Point2D normalized_undistorted = { x, y };
    return normalized_undistorted;
}
