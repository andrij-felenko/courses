#include <cstdint>

namespace sec {

enum class Token : std::uint32_t {
    True  = 0x55AA55AAU,
    False = 0xAA55AA55U,
    Init  = 0x3C3C3C3CU,
    Panic = 0xFFFFFFFFU
};

} // namespace sec
