#include <cstdint>

namespace link_api {

#pragma pack(push, 1)
struct MuxFrameHeader {
    uint8_t     version{1};
    BearerId    bearerId{BearerId::Primary};
    QosPriority qosPrio{QosPriority::CriticalCommand};
    uint8_t     flags{0};
    uint16_t    sequenceNum{0};
    uint16_t    payloadLen{0};
};
#pragma pack(pop)

} // namespace link_api
