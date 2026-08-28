namespace physics::mechanics {

class NewtonOrbitFinder {
public:
    [[nodiscard]] static std::expected<Point2D, MappingStatus> findPeriodicPoint(const HorseshoeMap& map,
                                                                                 std::span<const int> code) {
        return map.reconstructFromSymbolicCode(code, code);
    }
};

}
