// груба поза з ≥6 пар, без початкового здогаду
Pose dlt(const Camera& cam, const std::vector<Corr>& pts) {
    const int n = (int)pts.size();
    MatrixXd A(2 * n, 12);
    for (int i = 0; i < n; ++i) {
        // прибираємо K: працюємо в нормованих координатах променя
        double x = (pts[i].uv.x() - cam.cx) / cam.fx;
        double y = (pts[i].uv.y() - cam.cy) / cam.fy;
        const Vector3d& X = pts[i].X;
        A.row(2 * i)     << X.x(), X.y(), X.z(), 1,  0, 0, 0, 0,
                            -x * X.x(), -x * X.y(), -x * X.z(), -x;
        A.row(2 * i + 1) << 0, 0, 0, 0,  X.x(), X.y(), X.z(), 1,
                            -y * X.x(), -y * X.y(), -y * X.z(), -y;
    }
    // нуль-простір: правий сингулярний вектор найменшого сингулярного числа
    Eigen::JacobiSVD<MatrixXd> svd(A, Eigen::ComputeThinV);
    VectorXd p = svd.matrixV().col(11);

    Matrix3d M;
    M << p(0), p(1), p(2),
         p(4), p(5), p(6),
         p(8), p(9), p(10);
    Vector3d d(p(3), p(7), p(11));

    // глобальний знак: правильна M = γ·R має det = γ³ > 0, дзеркальний двійник −M — від'ємний
    if (M.determinant() < 0) { M = -M; d = -d; }

    // найближчий поворот і масштаб — через SVD матриці M ≈ γ·R
    Eigen::JacobiSVD<Matrix3d> ms(M, Eigen::ComputeFullU | Eigen::ComputeFullV);
    double gamma = ms.singularValues().mean();          // усі три ≈ γ, бо R ортонормована
    Matrix3d R = ms.matrixU() * ms.matrixV().transpose();
    if (R.determinant() < 0) {                          // рідкісний випадок від шуму
        Matrix3d V = ms.matrixV();  V.col(2) *= -1;
        R = ms.matrixU() * V.transpose();
    }
    return { R, d / gamma };
}
