#include <cstdint>
#include <new>

namespace stats {

template <typename FloatType = double>
struct alignas(64) AlignedAccumulatorState {
    std::uint64_t count{0};
    FloatType mean{0.0};
    FloatType M2{0.0};
    FloatType M3{0.0};
    FloatType M4{0.0};
    FloatType min_val{0.0};
    FloatType max_val{0.0};
};

} // namespace stats
