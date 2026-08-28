#include <cstdint>

namespace takens {
enum class Status : int32_t {
    Ok                  =  0,
    NullPointer         = -1,
    InvalidParam        = -2,
    SignalTooShort      = -3,
    OutOfMemory         = -4,
    NoMinimumFound      = -5,
    FnnConvergenceError = -6,
    ZeroVariance        = -7
};
}
