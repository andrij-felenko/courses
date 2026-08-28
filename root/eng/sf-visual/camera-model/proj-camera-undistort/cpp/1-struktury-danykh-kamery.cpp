#include <cstdint>
#include <cmath>
#include <vector>
#include <span>
#include <array>
#include <memory>
#include <algorithm>

namespace vision {

// Внутрішні параметри камери
struct CameraIntrinsics {
    double fx{0.0};     // фокусна відстань за віссю X (у пікселях)
    double fy{0.0};     // фокусна відстань за віссю Y (у пікселях)
    double cx{0.0};     // координата X головної точки
    double cy{0.0};     // координата Y головної точки
};

// Коефіцієнти дисторсії Брауна–Конраді
struct DistortionCoeffs {
    double k1{0.0};     // радіальний коефіцієнт 1
    double k2{0.0};     // радіальний коефіцієнт 2
    double k3{0.0};     // радіальний коефіцієнт 3
    double p1{0.0};     // тангенціальний коефіцієнт 1
    double p2{0.0};     // тангенціальний коефіцієнт 2
};

struct Point2D {
    double x{0.0};
    double y{0.0};
};

struct Point3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};
};

} // namespace vision
