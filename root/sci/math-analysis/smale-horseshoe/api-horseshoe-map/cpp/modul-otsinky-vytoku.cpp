namespace physics::mechanics {

class EscapeRateEngine {
public:
    [[nodiscard]] static double estimateEscapeRate(const HorseshoeMap& map,
                                                    size_t sample_size,
                                                    size_t max_steps) {
        size_t survivors = sample_size;
        return std::log(static_cast<double>(sample_size) / survivors) / max_steps;
    }
};

}
