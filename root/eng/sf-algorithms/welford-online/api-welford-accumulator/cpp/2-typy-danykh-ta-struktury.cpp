#include <cstdint>
#include <limits>

namespace stats {

template <typename FloatType = double>
struct AccumulatorState {
    std::uint64_t count{0};
    FloatType mean{0.0};
    FloatType M2{0.0};
    FloatType M3{0.0};
    FloatType M4{0.0};
    FloatType min_val{std::numeric_limits<FloatType>::infinity()};
    FloatType max_val{-std::numeric_limits<FloatType>::infinity()};
};

} // namespace stats
