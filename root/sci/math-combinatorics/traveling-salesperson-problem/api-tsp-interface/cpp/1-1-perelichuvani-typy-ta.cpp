#include <cstdint>

namespace tsp {

enum class MetricType : uint8_t {
    Euclidean2D = 0,
    Manhattan   = 1,
    General     = 2,
    Asymmetric  = 3
};

enum class Algorithm : uint8_t {
    HeldKarp       = 0,
    BranchAndBound = 1,
    Christofides   = 2,
    LocalSearch2Opt= 3
};

enum class Status : int8_t {
    Success          =  0,
    InvalidParameter = -1,
    NonMetric        = -2,
    Timeout          = -3,
    OutOfMemory      = -4,
    Overflow         = -5
};

} // namespace tsp
