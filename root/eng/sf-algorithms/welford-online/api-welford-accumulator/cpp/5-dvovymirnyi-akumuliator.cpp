#include <cstdint>
#include <cmath>

namespace stats {

template <typename FloatType = double>
class CovarianceAccumulator {
public:
    constexpr CovarianceAccumulator() noexcept = default;
    void push(FloatType x, FloatType y) noexcept;
    [[nodiscard]] FloatType covariance() const noexcept;
    [[nodiscard]] FloatType correlation() const noexcept;
    [[nodiscard]] std::uint64_t count() const noexcept;

private:
    std::uint64_t count_{0};
    FloatType mean_x_{0.0};
    FloatType mean_y_{0.0};
    FloatType M2_x_{0.0};
    FloatType M2_y_{0.0};
    FloatType C_xy_{0.0};
};

} // namespace stats
