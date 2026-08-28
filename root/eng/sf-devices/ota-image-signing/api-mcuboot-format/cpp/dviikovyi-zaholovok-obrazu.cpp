#include <cstdint>

namespace mcuboot {

struct ImageVersion {
    uint8_t  major{0};
    uint8_t  minor{0};
    uint16_t revision{0};
    uint32_t build_num{0};
};

struct alignas(4) ImageHeader {
    uint32_t magic{0};
    uint32_t load_addr{0};
    uint16_t hdr_size{0};
    uint16_t protect_tlv_size{0};
    uint32_t img_size{0};
    uint32_t flags{0};
    ImageVersion ver{};
    uint32_t reserved{0};
};

} // namespace mcuboot
