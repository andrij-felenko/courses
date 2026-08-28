namespace physics::mechanics {

struct Point3D {
    double x, y, z;
};

class PoincareSectionEvaluator {
public:
    [[nodiscard]] static Point3D computeSection(const Point3D& pt, double period) noexcept {
        return pt;
    }
};

}
