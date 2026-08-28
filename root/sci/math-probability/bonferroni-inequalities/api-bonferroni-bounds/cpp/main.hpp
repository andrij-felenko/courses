#ifndef BONFERRONI_BOUNDS_HPP
#define BONFERRONI_BOUNDS_HPP

#include <vector>
#include <functional>
#include <span>
#include <expected>
#include <system_error>

namespace bonferroni {

enum class ErrorCode {
    InvalidParameter = 1,
    OutOfMemory,
    OracleFailure,
    PrecisionLoss,
    BufferTooSmall
};

std::error_code make_error_code(ErrorCode ec);

struct Config {
    size_t maxOrder{2};
    double targetPrecision{1e-5};
    bool autoEarlyStop{true};
};

struct BoundsResult {
    double upperBound{1.0};
    double lowerBound{0.0};
    std::vector<double> sTerms;
    size_t evaluatedOrder{0};

    [[nodiscard]] double gap() const noexcept {
        return upperBound - lowerBound;
    }
};

using OracleFunction = std::function<double(std::span<const size_t>)>;

class Evaluator {
public:
    explicit Evaluator(Config config = {}) : config_(config) {}

    [[nodiscard]] std::expected<BoundsResult, ErrorCode> compute(
        size_t eventCount, 
        const OracleFunction& oracle
    ) const;

private:
    Config config_;
};

} // namespace bonferroni

#endif /* BONFERRONI_BOUNDS_HPP */
