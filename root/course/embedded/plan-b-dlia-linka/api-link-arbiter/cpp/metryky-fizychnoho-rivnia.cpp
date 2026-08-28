#include <chrono>

namespace link_api {

struct BearerMetrics {
    int16_t  rssiDbm{-120};
    int8_t   snrDb{-20};
    uint8_t  perPercent{100};
    uint16_t rttMs{0};
    uint32_t throughputBps{0};
    std::chrono::milliseconds lastRxMono{0};
    uint8_t  compositeScore{0};
    bool     isLinkAlive{false};
};

} // namespace link_api
