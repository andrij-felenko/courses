namespace physics::mechanics {

class SimdVectorEvaluator {
public:
    static void forwardBatch(std::span<const double> x_in,
                             std::span<const double> y_in,
                             std::span<double> x_out,
                             std::span<double> y_out,
                             const Config& config) noexcept {
        const size_t count = x_in.size();
        for (size_t i = 0; i < count; ++i) {
            x_out[i] = config.alpha * x_in[i];
            y_out[i] = config.beta * y_in[i];
        }
    }
};

}
