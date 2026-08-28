#include <cstdint>

namespace stats {

enum class Status : std::uint8_t {
    Ok = 0,
    NullPointer = 1,
    InsufficientData = 2,
    DegenerateSample = 3,
    NanInput = 4
};

} // namespace stats
