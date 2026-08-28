namespace physics::mechanics {

struct HenonParams {
    double a{1.4};
    double b{0.3};
};

class HenonMapEvaluator {
public:
    [[nodiscard]] static Point2D forward(const Point2D& pt, const HenonParams& params) noexcept {
        return Point2D{1.0 - params.a * pt.x * pt.x + pt.y, params.b * pt.x};
    }
};

}
