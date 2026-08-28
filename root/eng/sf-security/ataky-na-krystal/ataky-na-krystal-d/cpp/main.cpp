#include <cstdint>

namespace sec {

enum class SecureBool : std::uint32_t {
    True  = 0x55AA55AAU,
    False = 0xAA55AA55U
};

} // namespace sec
