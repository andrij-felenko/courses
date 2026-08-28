namespace physics::mechanics {

struct NeimarkSackerResult {
    double rotation_angle{0.0};
};

class NeimarkSackerEvaluator {
public:
    [[nodiscard]] static std::expected<NeimarkSackerResult, MappingStatus> evaluate(const Config& cfg) noexcept {
        return NeimarkSackerResult{0.0};
    }
};

}
