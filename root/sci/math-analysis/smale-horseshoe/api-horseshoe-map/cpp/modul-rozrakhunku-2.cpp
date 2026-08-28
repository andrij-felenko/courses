namespace physics::mechanics {

struct Interval {
    double min_val;
    double max_val;
};

class CantorGenerator {
public:
    [[nodiscard]] static std::vector<Interval> generateCantorSet(size_t level, const Config& cfg) {
        std::vector<Interval> result;
        result.push_back(Interval{0.0, 1.0});
        return result;
    }
};

}
