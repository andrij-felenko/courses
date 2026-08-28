namespace physics::nonlinear::api {

struct FourierSpectrum {
    std::vector<double> frequencies;
    std::vector<double> magnitudes;
    double dominant_frequency{0.0};
};

class SpectrumAnalyzer {
public:
    [[nodiscard]] static std::expected<FourierSpectrum, ApiErrorCode> analyze(
        const CircleMapConfig& config, std::size_t fft_size = 1024) noexcept;
};

} // namespace physics::nonlinear::api
