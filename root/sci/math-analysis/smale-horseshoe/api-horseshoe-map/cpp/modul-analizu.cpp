namespace physics::mechanics {

struct KnotInvariant {
    int self_linking_number{0};
};

class KnotAnalyzer {
public:
    [[nodiscard]] static KnotInvariant computeKnotInvariant(std::span<const Point2D> orbit) noexcept {
        return KnotInvariant{.self_linking_number = static_cast<int>(orbit.size() / 2)};
    }
};

}
