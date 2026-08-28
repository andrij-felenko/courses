#include <cstdint>

namespace mcuboot {

struct alignas(2) TlvInfo {
    uint16_t magic{0};
    uint16_t total_len{0};
};

struct alignas(2) TlvItem {
    uint16_t type{0};
    uint16_t len{0};
};

} // namespace mcuboot
