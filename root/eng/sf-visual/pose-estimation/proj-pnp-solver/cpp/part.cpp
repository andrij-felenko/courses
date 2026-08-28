#include <Eigen/Dense>
#include <vector>
#include <random>
#include <cmath>
#include <algorithm>

using Eigen::Matrix3d;  using Eigen::Vector3d;  using Eigen::Vector2d;
using Eigen::MatrixXd;  using Eigen::VectorXd;

struct Camera { double fx, fy, cx, cy; };          // внутрішні параметри (матриця K)
struct Corr   { Vector3d X;  Vector2d uv; };        // 3D-точка світу ↔ спостережений піксель
struct Pose   { Matrix3d R;  Vector3d t; };         // X_камери = R·X_світу + t

// кососиметрична матриця вектора:  [w]× · v  =  w × v
static Matrix3d skew(const Vector3d& w) {
    Matrix3d S;
    S <<     0, -w.z(),  w.y(),
         w.z(),      0, -w.x(),
        -w.y(),  w.x(),      0;
    return S;
}

// експонента SO(3): вектор осі-кута → матриця повороту (формула Родриґа)
static Matrix3d expSO3(const Vector3d& w) {
    double th = w.norm();
    if (th < 1e-12) return Matrix3d::Identity();
    Matrix3d K = skew(w / th);
    return Matrix3d::Identity() + std::sin(th) * K + (1 - std::cos(th)) * K * K;
}

// проєкція точки світу в піксель за поточної пози (дорога вперед)
static Vector2d project(const Camera& c, const Pose& P, const Vector3d& X) {
    Vector3d Xc = P.R * X + P.t;
    return { c.fx * Xc.x() / Xc.z() + c.cx,
             c.fy * Xc.y() / Xc.z() + c.cy };
}
